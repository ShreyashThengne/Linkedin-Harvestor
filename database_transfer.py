import datetime
import psycopg2
import pandas as pd
import logging

logger = logging.getLogger(__name__)
handler = logging.FileHandler('logs.log')
formattor = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formattor)
logger.addHandler(handler)


db_name = 'linkedin database'
db_user = 'postgres'
db_pass = "Shreyash2003"
db_host = "localhost"
db_port = "5432"

try:
    conn = psycopg2.connect(
        database=db_name,
        user=db_user,
        password=db_pass,
        host=db_host,
        port=db_port
    )
    print("Database connected successfully")
except:
    logger.error("Database not connected successfully")

curr = conn.cursor()

def get_current_output(curr = curr):
    rows = []
    for i in curr.fetchall():
        rows.append(i)
    return rows

def query(query, values = ()):
    '''Any query, except select statement'''
    
    conn.rollback()
    curr.execute(query, values)
    conn.commit()

def select_query(query, values = ()):
    conn.rollback()
    curr.execute(query, values)
    conn.commit()
    return get_current_output()

def send_to_database(data):
    for profile in data:
        try:
            query("INSERT INTO name_table(name) values(%s)", (profile['data']['contact']['name'],))
        except: 
            pass
        try:
            query("INSERT INTO city_table(city) values(%s)", (profile['data']['contact']['city'],))
        except:
            profile['data']['contact']['city']
            pass
        
        contact = profile['data']['contact']

        name_id = select_query(f"select name_id from name_table where name = %s", (contact['name'],))[0][0]
        city_id = select_query(f"select city_id from city_table where city = %s", (contact['city'],))[0][0]
        
        followers = int("".join(profile['data']['followers'].split(",")))
        

        query('''INSERT INTO profile_table(name_id, p_link, city_id, website, email, im, phone, connections, followers, about)
        Values(
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )''', (name_id, contact['profile_link'], city_id, contact['Website'], contact['Email'], contact['IM'], contact['Phone'], profile['data']['connections'], followers, profile['data']['about'],)
        )


        # p_lang_table
        p_id = select_query("SELECT max(p_id) FROM profile_table")[0][0]  # as max will be the most recently used p_id (ikik 😅)
        for l in profile['data']['languages']:
            try:
                lang_id = select_query("SELECT lang_id FROM lang_table where language = %s", (l['language'],))[0][0]
                query("INSERT INTO p_lang_table VALUES(%s, %s, %s)", (p_id, lang_id, l['profiency'],))
            except:
                pass
        
        # p_award_table
        for l in profile['data']['awards']:
            try:
                award_sk = select_query("SELECT award_sk FROM award_table where award_org = %s and award_name = %s", (l['org'], l['award_name'],))[0][0]
                query("INSERT INTO p_award_table VALUES(%s, %s, %s)", (p_id, award_sk, l['date'],))
                query("INSERT INTO date_table VALUES(%s, %s, %s, %s)", (l['date'], l['date'].day, l['date'].month, l['date'].year))
            except:
                pass


        # p_cert_table
        for l in profile['data']['certification']:
            try:
                cert_sk = select_query("SELECT cert_sk FROM cert_table where cert_org = %s and cert_name = %s", (l['cert_org'], l['cert_name'],))[0][0]
                query("INSERT INTO p_cert_table VALUES(%s, %s, %s, %s)", (p_id, cert_sk, l['cert_issued'], l['cert_link']))
            except:
                pass
        
        # p_skills_table
        for l in profile['data']['skills']:
            try:
                skill_id = select_query("SELECT skill_id FROM skills_table where skill_name = %s", (l,))[0][0]
                query("INSERT INTO p_skills_table VALUES(%s, %s)", (p_id, skill_id))
            except:
                pass
        
        # p_exp_table
        for l in profile['data']['experience']:
            try:
                company_id = select_query("SELECT company_id FROM company_table where company_name = %s", (l['company'],))[0][0]
                role_id = select_query("SELECT role_id FROM role_table where role_name = %s", (l['role'],))[0][0]
                query("INSERT INTO p_exp_table VALUES(%s, %s, %s, %s, %s, %s, %s)", (p_id, company_id, role_id, l['job_type'], l['from_date'], l['to_date'], l['duration']))
            except:
                pass
        
        # p_edu_table
        for l in profile['data']['education']:
            try:
                college_id = select_query("SELECT college_id FROM college_table where college_name = %s", (l['college'],))[0][0]
                degree_id = select_query("SELECT degree_id FROM degree_table where degree_name = %s", (l['degree'],))[0][0]
                query("INSERT INTO p_edu_table VALUES(%s, %s, %s, %s, %s)", (p_id, college_id, degree_id, l['from'], l['to'],))
            except:
                pass
        




        # lang_table
        langs = []
        for profile in data:
            for l in profile['data']['languages']:
                try:
                    query("INSERT INTO lang_table(language) values(%s)", (l['language'],))
                except:  # already exist
                    pass

        # # award_table
        award = []
        for profile in data:
            for a in (profile['data']['awards']):
                try:
                    query("INSERT INTO award_table(award_org, award_name) values(%s, %s)", (a['org'], a['award_name'],))
                except:  # already exist
                    pass

        # cert_table
        cert = []
        for profile in data:
            for c in profile['data']['certification']:
                try:
                    query("INSERT INTO cert_table(cert_org, cert_name) values(%s, %s)", (c['cert_org'], c['cert_name'],))
                except:  # already exist
                    pass

        # skills_table
        skills = []
        for profile in data:
            for s in profile['data']['skills']:
                try:
                    query("INSERT INTO skills_table(skill_name) values(%s)", (s,))
                except:  # already exist
                    pass

        # company_table
        exp = []
        for profile in data:
            for s in profile['data']['experience']:
                try:
                    query("INSERT INTO company_table(company_name) values(%s)", (s['company'],))
                    query("INSERT INTO role_table(role_name) values(%s)", (s['role'],))
                except:  # already exist
                    pass

        # college_table
        edu = []
        for profile in data:
            for s in profile['data']['education']:
                try:
                    query("INSERT INTO college_table(college_name) values(%s)", (s['college'],))
                    query("INSERT INTO degree_table(degree_name) values(%s)", (s['degree'],))
                except:  # already exist
                    pass