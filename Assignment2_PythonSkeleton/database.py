#!/usr/bin/env python3
import psycopg2
import db_info

#####################################################
##  Database Connection
#####################################################

'''
Connect to the database using the connection string
'''


class PythonClient:
    # connection parameters - ENTER YOUR LOGIN AND PASSWORD HERE
    # initializer
    def __init__(self):
        self.userid = db_info.userid
        self.passwd = db_info.passwd
        self.myHost = db_info.myHost
        self.conn = None

    # Establishes a connection to the database.
    # The connection parameters are read from the instance variables above
    # (userid, passwd, and database).
    # @returns  true   on success and then the instance variable 'conn'
    # holds an open connection to the database.
    # false  otherwise
    #
    def connectToDatabase(self):
        print("Connecting to the database...")
        try:
            # connect to the database
            self.conn = psycopg2.connect(database=self.userid,
                                         user=self.userid,
                                         password=self.passwd,
                                         host=self.myHost
                                         )
            print("Connected to database")
            return True

        except psycopg2.Error as sqle:
            print("psycopg2.Error : " + sqle.pgerror)
            return False

    # close the database connection
    def closeConnection(self):
        print("Closing database connection...")
        if self.conn is None:
            print("You are not connected to the database!")
        else:
            try:
                self.conn.close()  # close the connection again after usage!
                self.conn = None
                print("Disconnected to database")
            except psycopg2.Error as sqle:
                print("psycopg2.Error : " + sqle.pgerror)

    def isConnected(self):
        return self.conn is not None

    def cursor(self):
        return self.conn.cursor()

    def commit(self):
        self.conn.commit()

    def __del__(self):
        if self.isConnected():
            self.closeConnection()


'''
Validate staff based on username and password
'''
def checkStaffLogin(staffID, password):

    python_client = PythonClient()
    if python_client.connectToDatabase():
        cur = python_client.cursor()
        cur.execute("SELECT * FROM staff WHERE staffid = %s AND password = %s", (staffID, password))
        user_info = cur.fetchone()
        python_client.commit()
        cur.close()
    else:
        user_info = None
    python_client.closeConnection()
    return user_info


'''
List all the associated menu items in the database by staff
'''
def findMenuItemsByStaff(staffID):
    python_client = PythonClient()
    menuitems = []
    if python_client.connectToDatabase():
        cur = python_client.cursor()
        cur.execute("""
            SELECT menuitemid, name, 
    CASE
        WHEN description IS NOT NULL THEN description
        ELSE ''
    END description,
    CASE
        WHEN c1.categoryname IS NOT NULL THEN c1.categoryname
        ELSE ''
    END
    || CASE
        WHEN c2.categoryname IS NOT NULL THEN '|' || c2.categoryname
        ELSE ''
    END
    || CASE
        WHEN c3.categoryname IS NOT NULL THEN '|' || c3.categoryname
        ELSE ''
    END AS Category,
    CASE
        WHEN co.coffeetypename IS NOT NULL THEN co.coffeetypename
        ELSE  ''
    END
    || CASE
        WHEN mi.milkkindname IS NOT NULL THEN ' - ' || mi.milkkindname
        ELSE ''
    END AS Option,
    price,
    CASE 
        WHEN reviewdate IS NOT NULL THEN TO_CHAR(reviewdate, 'DD-MM-YYYY')
        ELSE ''
    END As ReviewDate,
    COALESCE(s.firstname,'') ||' '|| COALESCE(s.lastname, '') as reviewer

FROM menuitem m
LEFT JOIN category c1 ON m.categoryone = c1.categoryid
LEFT JOIN category c2 ON m.categorytwo = c2.categoryid
LEFT JOIN category c3 ON m.categorythree = c3.categoryid
LEFT JOIN coffeetype co ON m.coffeetype = co.coffeetypeid
LEFT JOIN milkkind mi ON m.milkkind = mi.milkkindid
LEFT JOIN staff s ON s.staffid = m.reviewer
WHERE reviewer = %s 
ORDER BY reviewdate ASC, CASE WHEN COALESCE(description,'') = '' THEN 0 ELSE 1 END ASC, description ASC, price DESC
        """, (staffID,))
        menuitem_info = cur.fetchall()
        for menuitem in menuitem_info:
            menuitems.append({
                'menuitem_id': menuitem[0],
                'name': menuitem[1],
                'description': menuitem[2],
                'category': menuitem[3],
                'coffeeoption': menuitem[4],
                'price': menuitem[5],
                'reviewdate': menuitem[6],
                'reviewer': menuitem[7]
            })
        python_client.commit()
        cur.close()
    else:
        menuitems = None
    python_client.closeConnection()
    return menuitems


'''
Find a list of menu items based on the searchString provided as parameter
See assignment description for search specification
'''
def findMenuItemsByCriteria(searchString):
    python_client = PythonClient()
    menuitems = []
    if python_client.connectToDatabase():
        cur = python_client.cursor()
        cur.execute("""
        SELECT *
FROM (
    SELECT menuitemid, name, 
    CASE
        WHEN description IS NOT NULL THEN description
        ELSE ''
    END description,
    CASE
        WHEN c1.categoryname IS NOT NULL THEN c1.categoryname
        ELSE ''
    END
    || CASE
        WHEN c2.categoryname IS NOT NULL THEN '|' || c2.categoryname
        ELSE ''
    END
    || CASE
        WHEN c3.categoryname IS NOT NULL THEN '|' || c3.categoryname
        ELSE ''
    END AS Category,
    CASE
        WHEN co.coffeetypename IS NOT NULL THEN co.coffeetypename
        ELSE  ''
    END
    || CASE
        WHEN mi.milkkindname IS NOT NULL THEN ' - ' || mi.milkkindname
        ELSE ''
    END AS Option,
    price,
    CASE 
        WHEN reviewdate IS NOT NULL THEN TO_CHAR(reviewdate, 'DD-MM-YYYY')
        ELSE ''
    END As ReviewDate,
    COALESCE(s.firstname,'') ||' '|| COALESCE(s.lastname, '') as reviewer

FROM menuitem m
LEFT JOIN category c1 ON m.categoryone = c1.categoryid
LEFT JOIN category c2 ON m.categorytwo = c2.categoryid
LEFT JOIN category c3 ON m.categorythree = c3.categoryid
LEFT JOIN coffeetype co ON m.coffeetype = co.coffeetypeid
LEFT JOIN milkkind mi ON m.milkkind = mi.milkkindid
LEFT JOIN staff s ON s.staffid = m.reviewer
ORDER BY reviewdate ASC, description ASC, price DESC
     ) as m
WHERE (m.name ILIKE concat_with_wildcards(%s)
OR m.description ILIKE concat_with_wildcards(%s)
OR m.category ILIKE concat_with_wildcards(%s)
OR m.option ILIKE concat_with_wildcards(%s)
OR m.reviewer ILIKE concat_with_wildcards(%s))
AND ((TO_DATE(m.reviewdate, 'DD-MM-YYYY') >= CURRENT_DATE - INTERVAL '10 years') OR (m.reviewdate IS NULL) OR (m.reviewdate = ''))
ORDER BY 
    CASE WHEN m.reviewer = '' OR m.reviewer IS NULL THEN 0 ELSE 1 END ASC,
    CASE WHEN m.reviewdate <> '' AND m.reviewdate IS NOT NULL THEN TO_DATE(m.reviewdate, 'DD-MM-YYYY') END DESC;        """, (searchString, searchString, searchString, searchString, searchString))
        menuitem_info = cur.fetchall()
        print(menuitem_info)
        for menuitem in menuitem_info:
            menuitems.append({
                'menuitem_id': menuitem[0],  # menuitemid
                'name': menuitem[1],  # name
                'description': menuitem[2],  # description
                'category': menuitem[3],  # category
                'coffeeoption': menuitem[4],  # option
                'price': menuitem[5],  # price
                'reviewdate': menuitem[6],  # reviewdate
                'reviewer': menuitem[7]  # reviewer
            })
        python_client.commit()
        cur.close()
    else:
        menuitems = None
    python_client.closeConnection()
    return menuitems


'''
Add a new menu item
'''
def addMenuItem(name, description, categoryone, categorytwo, categorythree, coffeetype, milkkind, price):
    python_client = PythonClient()
    if python_client.connectToDatabase():
        cur = python_client.cursor()
        try:
            cur.execute(
            """
                INSERT INTO menuitem (name, description, categoryone, categorytwo, categorythree, coffeetype, milkkind, price, reviewdate)
                VALUES(
                    %s,
                    %s,
                    (SELECT categoryid FROM category WHERE lower(categoryname) = lower(%s)),
                    (SELECT categoryid FROM category WHERE lower(categoryname) = lower(%s)),
                    (SELECT categoryid FROM category WHERE lower(categoryname) = lower(%s)),
                    (SELECT coffeetypeid FROM coffeetype WHERE lower(coffeetypename) = lower(%s)),
                    (SELECT milkkindid FROM milkkind WHERE lower(milkkindname) = lower(%s)),
                    %s,
                    CURRENT_DATE
                    )
                """, (name, description, categoryone, categorytwo, categorythree, coffeetype, milkkind, price))
        except:
            return False

        python_client.commit()
        cur.close()
        python_client.closeConnection()
        return True
    else:
        python_client.closeConnection()
        return False


'''
Update an existing menu item
'''
def updateMenuItem(menu_item_id, name, description, categoryone, categorytwo, categorythree, coffeetype, milkkind, price, reviewdate, reviewer):
    python_client = PythonClient()
    if python_client.connectToDatabase():
        cur = python_client.cursor()
        try:
            cur.execute(
                """
                    UPDATE menuitem 
                    SET 
                        name = %s,
                        description = %s,
                        categoryone = (SELECT categoryid FROM category WHERE lower(categoryname) = lower(%s)),
                        categorytwo = (SELECT categoryid FROM category WHERE lower(categoryname) = lower(%s)),
                        categorythree = (SELECT categoryid FROM category WHERE lower(categoryname) = lower(%s)),
                        coffeetype = (SELECT coffeetypeid FROM coffeetype WHERE lower(coffeetypename) = lower(%s)),
                        milkkind = (SELECT milkkindid FROM milkkind WHERE lower(milkkindname) = lower(%s)),
                        price = %s,
                        reviewDate = %s,
                        reviewer = REPLACE(LOWER(%s), ' ', '')
                    WHERE 
                        MenuItemID = %s;
                    """, (name, description, categoryone, categorytwo, categorythree, coffeetype, milkkind, price, reviewdate,
                reviewer, menu_item_id))
            python_client.commit()
            cur.close()
            python_client.closeConnection()
            return True

        except Exception as e:
            print(e)
            python_client.closeConnection()
            return False


def main():
    pythonClient = PythonClient()
    pythonClient.closeConnection()

    print(findMenuItemsByStaff("1223"))
    # pythonClient = PythonClient()
    #
    # # execute commands
    # cur = pythonClient.conn.cursor()
    #
    # # do something
    # # cur.execute("""
    # # CREATE TABLE IF NOT EXISTS person(
    # # 	id INT PRIMARY KEY,
    # # 	name VARCHAR(255),
    # # 	age INT,
    # # 	gender CHAR
    # # )
    # # """)
    # # cur.execute("""
    # #     Insert into person(id, name, age, gender) values (124, 'Juan', 32, 'm')
    # # """
    # # )
    #
    # pythonClient.conn.commit()
    #
    # cur.close()
    # pythonClient.closeConnection()

if __name__ == "__main__":
    main()
