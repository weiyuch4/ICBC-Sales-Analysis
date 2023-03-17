from datetime import datetime
from datetime import date
import pyodbc


class SussexData:

    def __init__(self):
        os.chdir("..")
        parent_dir_path = os.path.abspath(os.curdir)
        self.conn = pyodbc.connect(
            r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
            rf'DBQ={parent_dir_path}\South Surrey.mdb;'
        )
        self.cur = self.conn.cursor()
        os.chdir(f"{parent_dir_path}\RENEWAL")

    def generate_mail_list(self):
        try:
            start_date_input_str = input("\nEnter Start Date (DD/MM/YYYY): ")
            start_date = datetime.strptime(start_date_input_str, '%d/%m/%Y')

            end_date_input_str = input("\nEnter End Date (DD/MM/YYYY): ")
            end_date = datetime.strptime(end_date_input_str, '%d/%m/%Y')

            if start_date <= end_date:
                query = (
                    f"""select c.lastname, c.firstname, c.address, c.city, c.postalcode, 
                    pd.expiry, pd.year, pd.made, pd.model, pn.plate, pn.rodl, c.notes 
                    from (clients c 
                    inner join [policy details] pd on c.policyno = pd.policyno) 
                    inner join [policy no] pn on pd.policyno = pn.policyno 
                    where (pd.expiry between #{start_date}# and #{end_date}#) and c.notification = 'Mail' 
                    and pn.plate is not null;"""
                )
                self.cur.execute(query)
                mail = self.cur.fetchall()

                return mail
            else:
                raise Exception("Start date must be earlier than end date")

        except Exception as err:
            print(f"Unexpected {err=}, {type(err)=}")

    def find_sales(self, target_date):
        try:
            str_date = target_date.strftime("%d %b, %Y")
            sql_date = datetime(target_date.year, target_date.month, target_date.day)

            query = (
                f"""select sum(l.premium), count(*) from ((clients c 
                inner join logs l on c.policyno = l.policyno) 
                inner join [policy details] pd on l.policyno = pd.policyno) 
                inner join producer p on pd.producerid = p.producerid
                where l.trandate = #{sql_date}#;"""
            )
            self.cur.execute(query)
            sales = self.cur.fetchall()[0]

            if sales[0] is None:
                sales[0] = 0

            return {'sales': round(sales[0], 2), 'transactions': sales[1], 'date': str_date}

        except Exception as err:
            print(f"Unexpected {err=}, {type(err)=}")

    def find_transactions_breakdown(self, target_date):
        try:
            sql_date = datetime(target_date.year, target_date.month, target_date.day)
            types = {'New Plate': 0, 'Renew': 0, 'Endorsement': 0, 'TOP': 0, 'Special Cvgs': 0}

            query = (
                f"""select pt.types, count(*) from ((clients c 
                inner join logs l on c.policyno = l.policyno) 
                inner join [policy details] pd on l.policyno = pd.policyno) 
                inner join [policy types] pt on l.typesid = pt.typesid
                where l.trandate = #{sql_date}# 
                group by pt.types;"""
            )
            self.cur.execute(query)
            transactions = self.cur.fetchall()

            for row in transactions:
                types[row[0]] = row[1]

            return types

        except Exception as err:
            print(f"Unexpected {err=}, {type(err)=}")

    def find_difference(self, date1, date2):
        try:
            d1_sales, d2_sales = self.find_sales(date1), self.find_sales(date2)
            d1_types, d2_types = self.find_transactions_breakdown(date1), self.find_transactions_breakdown(date2)

            sales_diff = d1_sales['sales'] - d2_sales['sales']
            transactions_diff = d1_sales['transactions'] - d2_sales['transactions']

            new_plates_diff = d1_types['New Plate'] - d2_types['New Plate']
            renewals_diff = d1_types['Renew'] - d2_types['Renew']
            endorsements_diff = d1_types['Endorsement'] - d2_types['Endorsement']
            top_diff = d1_types['TOP'] - d2_types['TOP']
            special_cov_diff = d1_types['Special Cvgs'] - d2_types['Special Cvgs']

            sales_table = [
                {
                    'Total Sales': ['$' + str(d1_sales['sales']), '$' + str(d2_sales['sales']), '$' + str(sales_diff)],
                    '# of Transactions': [d1_sales['transactions'], d2_sales['transactions'], transactions_diff]
                },
                [d1_sales['date'], d2_sales['date'], 'Difference']
            ]

            types_table = [
                {
                    d1_sales['date']: [d1_types['New Plate'], d1_types['Renew'], d1_types['Endorsement'], 
                                       d1_types['TOP'], d1_types['Special Cvgs']],
                    d2_sales['date']: [d2_types['New Plate'], d2_types['Renew'], d2_types['Endorsement'], 
                                       d2_types['TOP'], d2_types['Special Cvgs']],
                    'Difference': [new_plates_diff, renewals_diff, endorsements_diff, top_diff, special_cov_diff]
                },
                ['New Plates', 'Renewals', 'Endorsements', 'TOP', 'Special Coverages']
            ]

            return [sales_table, types_table]

        except Exception as err:
            print(f"Unexpected {err=}, {type(err)=}")

    def find_current_premiums(self):
        try:
            today = date.today()
            first_day_of_month = datetime(today.year, today.month, 1)
            str_first_day_of_month = first_day_of_month.strftime("%b %d, %Y")
            
            query = (
                f"""select sum(l.premium) from ((clients c 
                inner join logs l on c.policyno = l.policyno) 
                inner join [policy details] pd on l.policyno = pd.policyno) 
                inner join producer p on pd.producerid = p.producerid
                where l.trandate between #{first_day_of_month}# and #{today}#;"""
            )
            self.cur.execute(query)
            monthly_sales = self.cur.fetchall()[0][0]
            if monthly_sales is None:
                monthly_sales = 0

            first_day_of_year = datetime(today.year, 1, 1)
            str_first_day_of_year = first_day_of_year.strftime("%b %d, %Y")
            
            query = (
                f"""select sum(l.premium) from ((clients c 
                    inner join logs l on c.policyno = l.policyno) 
                    inner join [policy details] pd on l.policyno = pd.policyno) 
                    inner join producer p on pd.producerid = p.producerid
                    where l.trandate between #{first_day_of_year}# and #{today}#;"""
            )
            self.cur.execute(query)
            yearly_sales = self.cur.fetchall()[0][0]
            if yearly_sales is None:
                yearly_sales = 0

            sales_table = [
                {
                    "Total Sales": ['$' + str(round(monthly_sales, 2)), '$' + str(round(yearly_sales, 2))]
                },
                [f"From {str_first_day_of_month} to Today", f"From {str_first_day_of_year} to Today"]
            ]

            return sales_table

        except Exception as err:
            print(f"Unexpected {err=}, {type(err)=}")

    def get_yearly_sales(self, year):
        try:
            query = (
                f"""select month(l.trandate) as month_int, format(l.trandate, 'MMMM') as month, pt.types, 
                    sum(l.premium) as premiums 
                    from (((clients c inner join logs l on c.policyno = l.policyno) 
                    inner join [policy details] pd on l.policyno = pd.policyno) 
                    inner join producer p on pd.producerid = p.producerid) 
                    inner join [policy types] pt on l.typesid = pt.typesid
                    where year(l.trandate) = {year} 
                    group by format(l.trandate, 'MMMM'), month(l.trandate), pt.types order by month(l.trandate);"""
            )

            self.cur.execute(query)
            sales = self.cur.fetchall()

            columns = ['New Plate', 'Renew', 'Endorsement', 'TOP', 'Special Cvgs']
            table, months = [], []
            premiums = [0] * 5
            index = 0
            count_month = 1

            while count_month < 13 and index < len(sales):
                if count_month == sales[index][0]:
                    premiums[columns.index(sales[index][2])] = round(sales[index][3], 2)
                    index += 1
                else:
                    table.extend(premiums)
                    premiums = [0] * 5
                    months.extend([sales[index-1][1]] * 5)
                    count_month += 1
                if index == len(sales):
                    table.extend(premiums)
                    premiums = [0] * 5
                    months.extend([sales[index - 1][1]] * 5)
                    count_month += 1

            types = columns * (count_month-1)

            return {'Transaction Type': types, 'Premiums': table, 'Month': months}

        except Exception as err:
            print(f"Unexpected {err=}, {type(err)=}")

    def get_age_groups_premium(self):
        try:
            query = (
                f"""select pn.rodl, c.notes, sum(l.premium) as premiums 
                    from ((clients c 
                    inner join [policy details] pd on c.policyno = pd.policyno) 
                    inner join [policy no] pn on pd.policyno = pn.policyno) 
                    inner join logs l on pn.policyno = l.policyno 
                    where c.notes is not null 
                    group by pn.rodl, c.notes;"""
            )
            self.cur.execute(query)
            clients = self.cur.fetchall()

            age_groups = {
                'Under 16': [],
                '16-24': [],
                '25-34': [],
                '35-44': [],
                '45-54': [],
                '55-64': [],
                '65 and over': []
            }

            for client in clients:
                try:
                    dob_str = client[1].replace('-', '/')
                    dob = datetime.strptime(dob_str, '%d/%m/%y')
                    age = calculate_age(dob)

                    # Due to how the database is set up, there is no way to identify the correct year in some cases.
                    # For example, 01/01/20 could either represent Januray 1, 2020 or January 1, 1920.
                    # In cases like this, we are forced to assume that no one under the age of 10 owns a vehicle.
                    if age < 10:
                        age += 100

                    if age < 16:
                        age_groups['Under 16'].append(client[2])
                    elif 16 <= age <= 24:
                        age_groups['16-24'].append(client[2])
                    elif 25 <= age <= 34:
                        age_groups['25-34'].append(client[2])
                    elif 35 <= age <= 44:
                        age_groups['35-44'].append(client[2])
                    elif 45 <= age <= 54:
                        age_groups['45-54'].append(client[2])
                    elif 55 <= age <= 64:
                        age_groups['55-64'].append(client[2])
                    else:
                        age_groups['65 and over'].append(client[2])

                except ValueError:
                    print("Exception: there is an incorrect date of birth format")

            for key in age_groups:
                if len(age_groups[key]) > 0:
                    age_groups[key] = len(age_groups[key])
                else:
                    age_groups[key] = 0

            return {'Age Group': list(age_groups.keys()), 'Number of Clients': list(age_groups.values())}

        except Exception as err:
            print(f"Unexpected {err=}, {type(err)=}")

    def get_postal_code_breakdown(self):
        try:
            query = (
                f"""select left(c.postalcode, 3) as s, count(*) 
                    from clients c 
                    where c.postalcode is not null 
                    group by left(c.postalcode, 3) 
                    order by count(*) desc;"""
            )
            self.cur.execute(query)
            postal_codes = self.cur.fetchall()
            top_postal_codes = postal_codes[0:10]

            table = {
                'Postal Code': [],
                'Number of Clients': []
            }

            for item in top_postal_codes:
                table['Postal Code'].append(item[0])
                table['Number of Clients'].append(item[1])

            return table

        except Exception as err:
            print(f"Unexpected {err=}, {type(err)=}")


def calculate_age(birthday):
    today = datetime.today()
    try:
        day = birthday.replace(year=today.year)

    # When date of birth is February 29 and the current year is not a leap year
    except ValueError:
        day = birthday.replace(year=today.year,
                               month=birthday.month + 1, day=1)

    if day > today:
        return today.year - birthday.year - 1
    else:
        return today.year - birthday.year
