import datetime
import pyodbc
import os


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
            start_date = datetime.datetime.strptime(start_date_input_str, '%d/%m/%Y')

            end_date_input_str = input("\nEnter End Date (DD/MM/YYYY): ")
            end_date = datetime.datetime.strptime(end_date_input_str, '%d/%m/%Y')

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
                print("\nCount: " + str(len(mail)))
                return mail
            else:
                raise Exception("Start date must be earlier than end date")

        except Exception as err:
            print(f"Unexpected {err=}, {type(err)=}")

    def find_sales(self, date):
        try:
            tran_date = date.strftime("%d %b, %Y")
            sql_date = datetime.datetime(date.year, date.month, date.day)

            query = (
                f"""select l.premium from ((clients c 
                inner join logs l on c.policyno = l.policyno) 
                inner join [policy details] pd on l.policyno = pd.policyno) 
                inner join producer p on pd.producerid = p.producerid
                where trandate = #{sql_date}#;"""
            )
            self.cur.execute(query)
            premiums = self.cur.fetchall()

            sales = sum(i[0] for i in premiums)

            return {'sales': round(sales, 2), 'transactions': len(premiums), 'date': tran_date}

        except Exception as err:
            print(f"Unexpected {err=}, {type(err)=}")

    def find_transactions_breakdown(self, date):
        try:
            sql_date = datetime.datetime(date.year, date.month, date.day)
            breakdown = {'New Plate': 0, 'Renew': 0, 'Endorsement': 0, 'TOP': 0, 'Special Cvgs': 0}

            query = (
                f"""select pt.types, count(*) from ((clients c 
                inner join logs l on c.policyno = l.policyno) 
                inner join [policy details] pd on l.policyno = pd.policyno) 
                inner join [policy types] pt on l.typesid = pt.typesid
                where trandate = #{sql_date}# 
                group by pt.types;"""
            )
            self.cur.execute(query)
            all_trans = self.cur.fetchall()

            for transaction_type in all_trans:
                breakdown[transaction_type[0]] = transaction_type[1]

            return breakdown

        except Exception as err:
            print(f"Unexpected {err=}, {type(err)=}")

    def find_difference(self, date1, date2):
        try:
            day1_sales, day2_sales = self.find_sales(date1), self.find_sales(date2)
            day1_trans, day2_trans = self.find_transactions_breakdown(date1), self.find_transactions_breakdown(date2)

            sales_diff = day1_sales['sales'] - day2_sales['sales']
            transactions_diff = day1_sales['transactions'] - day2_sales['transactions']

            new_plates_diff = day1_trans['New Plate'] - day2_trans['New Plate']
            renewals_diff = day1_trans['Renew'] - day2_trans['Renew']
            endorsements_diff = day1_trans['Endorsement'] - day2_trans['Endorsement']
            top_diff = day1_trans['TOP'] - day2_trans['TOP']
            special_cov_diff = day1_trans['Special Cvgs'] - day2_trans['Special Cvgs']

            sales_table = [
                {
                    'Total Sales': ['$' + str(d1_sales['sales']), '$' + str(d2_sales['sales']), '$' + str(sales_diff)],
                    '# of Transactions': [day1_sales['transactions'], day2_sales['transactions'], transactions_diff]
                },
                [day1_sales['date'], day2_sales['date'], 'Difference']
            ]

            trans_table = [
                {
                    day1_sales['date']: [day1_trans['New Plate'], day1_trans['Renew'], day1_trans['Endorsement'],
                                         day1_trans['TOP'], day1_trans['Special Cvgs']],
                    day2_sales['date']: [day2_trans['New Plate'], day2_trans['Renew'], day2_trans['Endorsement'],
                                         day2_trans['TOP'], day2_trans['Special Cvgs']],
                    'Difference': [new_plates_diff, renewals_diff, endorsements_diff, top_diff, special_cov_diff]
                },
                ['New Plates', 'Renewals', 'Endorsements', 'TOP', 'Special Coverages']
            ]

            return [sales_table, trans_table]

        except Exception as err:
            print(f"Unexpected {err=}, {type(err)=}")

    def find_current_premiums(self):
        try:
            today = datetime.date.today()
            date_month = datetime.datetime(today.year, today.month, 1)
            date_year = datetime.datetime(today.year, 1, 1)

            query = (
                f"""select l.premium from ((clients c 
                inner join logs l on c.policyno = l.policyno) 
                inner join [policy details] pd on l.policyno = pd.policyno) 
                inner join producer p on pd.producerid = p.producerid
                where trandate between #{date_month}# and #{today}#;"""
            )
            self.cur.execute(query)
            premiums = self.cur.fetchall()

            monthly_sales = sum(i[0] for i in premiums)
            month_start_date = date_month.strftime("%b %d, %Y")

            query = (
                f"""select l.premium from ((clients c 
                    inner join logs l on c.policyno = l.policyno) 
                    inner join [policy details] pd on l.policyno = pd.policyno) 
                    inner join producer p on pd.producerid = p.producerid
                    where trandate between #{date_year}# and #{today}#;"""
            )
            self.cur.execute(query)
            premiums = self.cur.fetchall()

            yearly_sales = sum(i[0] for i in premiums)
            year_start_date = date_year.strftime("%b %d, %Y")

            sales_table = [
                {
                    "Total Sales": ['$' + str(round(monthly_sales, 2)), '$' + str(round(yearly_sales, 2))]
                },
                [f"From {month_start_date} to Today", f"From {year_start_date} to Today"]
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
            table = []
            months = []
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
                dob = datetime.datetime.strptime(dob_str, '%d/%m/%y')
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
                print("There is an incorrect date of birth format")

        for key in age_groups:
            if len(age_groups[key]) > 0:
                age_groups[key] = len(age_groups[key])
            else:
                age_groups[key] = 0

        return {'Age Group': list(age_groups.keys()), 'Number of Clients': list(age_groups.values())}

    def get_postal_code_breakdown(self):

        query = (
            f"""select left(c.postalcode, 3) as s, count(*) 
                from clients c 
                where c.postalcode is not null 
                group by left(c.postalcode, 3);"""
        )
        self.cur.execute(query)
        postal_codes = self.cur.fetchall()
        sorted_postal_codes = sorted(postal_codes, key=lambda postal: postal[1])
        sorted_postal_codes.reverse()
        top_postal_codes = sorted_postal_codes[0:10]

        table = {
            'Postal Code': [],
            'Number of Clients': []
        }

        for postal in top_postal_codes:
            table['Postal Code'].append(postal[0])
            table['Number of Clients'].append(postal[1])

        return table


def calculate_age(birthday):
    today = datetime.datetime.today()
    try:
        day = birthday.replace(year=today.year)

    # raised when date of birth is February 29
    # and the current year is not a leap year
    except ValueError:
        day = birthday.replace(year=today.year,
                               month=birthday.month + 1, day=1)

    if day > today:
        return today.year - birthday.year - 1
    else:
        return today.year - birthday.year

