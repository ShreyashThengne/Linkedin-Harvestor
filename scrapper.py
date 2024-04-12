import selenium  
from selenium import webdriver 
from selenium.webdriver.support.ui import WebDriverWait  
from selenium.webdriver.support import expected_conditions as ec 
from selenium.webdriver.common.action_chains import ActionChains 
from selenium.webdriver.common.keys import Keys 
from bs4 import BeautifulSoup  
from selenium.webdriver.common.by import By  
import time
from datetime import datetime
import logging


# setting up logging
logger = logging.getLogger(__name__)
handler = logging.FileHandler('logs.log')
formattor = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formattor)
logger.addHandler(handler)



driver = webdriver.Edge()
driver.get('https://www.linkedin.com/login')
actions = ActionChains(driver)

def create_soup(source_code):
    return BeautifulSoup(source_code, 'html.parser')


class Scraper:
    def __init__(self, id, pw):
        self.id = id
        self.pw = pw

    def login(self):
        driver.find_element(By.ID, "username").send_keys(self.id)
        driver.find_element(By.ID, "password").send_keys(self.pw)
        driver.find_element(By.CLASS_NAME, "login__form_action_container").click()
    
    def search(self, query):
        driver.find_element(By.ID, 'global-nav-search').click()
        actions.send_keys(query).send_keys(Keys.ENTER).perform()
        WebDriverWait(driver, 10).until(ec.presence_of_all_elements_located((By.CLASS_NAME, "search-reusables__primary-filter")))[0].click()
        actions.send_keys(Keys.ESCAPE).perform()
    
    def link_scraper(self, pages):
        profile_links = []
        for k in range(pages):
            # driver.implicitly_wait(10)
            time.sleep(page_delay)
            soup = create_soup(driver.page_source)

            for i in soup.find_all('li', {'class':"reusable-search__result-container"}):
                try:
                    profile_links.append(i.find('a',{'class':"app-aware-link scale-down"}).get('href'))
                except:
                    logger.info('Ad Encountered')

            actions.send_keys(Keys.END)
            time.sleep(page_delay)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.CLASS_NAME, "artdeco-pagination__button--next"))).click()
            
        return profile_links

    def run(self, query, pages):
        '''
        id, data (list->dict)
        '''
        
        self.search(query)
        profiles = self.link_scraper(pages)
        id = 1
        data = []
        for p in profiles:
            print("Extracting: ", p)
            profile_obj = Profile(p)
            data.append({
                'id':id,
                'data': profile_obj.get_all_the_data_my_slave()
            })
            id += 1 
        
        return data


page_delay = 3  # seconds
# this I am putting so that we will be able to capture the html code because page does not load the very instant
# it needs some time, varying with respect to speed of internet

class Profile:
    def __init__(self, link):
        driver.get(link)
        time.sleep(page_delay)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        self.profile_link = driver.current_url
        self.soup = create_soup(driver.page_source)
        self.cards = self.soup.find_all('section', {"class": "artdeco-card pv-profile-card break-words mt2"})
        self.sections_available = {}
        for i in self.cards:
            self.sections_available[i.find().get('id')] = True


    def get_contact_data(self):
        '''
        Website, Email, IM, Birthday, Connected, Address, Phone, name, profile_link (dict)
        '''

        try:
            # WebDriverWait(driver,10)
            name = self.soup.find('div', {'class', 'mt2 relative'}).findChild('h1',{'class':'text-heading-xlarge inline t-24 v-align-middle break-words'}).text

            driver.get(self.profile_link + 'overlay/contact-info/')
            obj_list = WebDriverWait(driver, 10).until(ec.presence_of_all_elements_located((By.CLASS_NAME, "pv-contact-info__contact-type")))
            contact_info = []
            for sel_obj in obj_list:
                contact_info.append(sel_obj.text.split("\n"))
            try:
                contact_info.remove(['Birthday'])
            except:
                pass

            def nested_list_to_dict(l):
                d = {}
                for i in l:
                    d[i[0]] = i[1]
                return d

            actions = ActionChains(driver)
            actions.send_keys(Keys.ESCAPE).perform()
            contact_info_dict = nested_list_to_dict(contact_info)
            if 'birthday' in contact_info_dict:
                contact_info_dict.pop('birthday')
            contact_info_dict['name'] = name

            if contact_info_dict == []:
                contact_info_dict = self.get_contact_data()
            
            city = self.soup.find("span", {'class':"text-body-small inline t-black--light break-words"}).text.strip()
            contact_info_dict['city'] = city
            contact_info_dict['profile_link'] = contact_info_dict[contact_info_dict['name'].split(" ")[0] + "’s " + 'Profile']
            contact_info_dict.pop(contact_info_dict['name'].split(" ")[0] + "’s " + 'Profile')

            for field in ['Website', 'Email', 'IM','Connected', 'city', 'Address', 'Phone', 'name', 'profile_link']:
                if field not in contact_info_dict:
                    contact_info_dict[field] = None
            return contact_info_dict
        
        except Exception as error:
            logger.error(error)
            return self.get_contact_data()
    

    def get_followers_and_about(self):
        '''
        connections, followers, about (tuple)
        '''
        
        about = None
        connections = None
        followers = None

        connections = self.soup.find('div', {'class', "mt2 relative"}).findNextSibling().text.strip()
        
        for i in self.cards:
            if i.find('div', {'id':'content_collections'}) != None:
                followers = i.find('div', {'class':'pvs-header__title-container'}).text.strip().split()[1]
                break

        for i in self.cards:
            if i.find('div', {'id':'about'}) != None:
                about = i.find('div', {'class':"display-flex ph5 pv3"}).text.strip()
                break

        if about != None:
            about = about[:len(about)//2]

        return connections, followers, about
    

    def get_experience(self):
        '''
        For all job roles: role, company, job_type, from, to, duration (list->dict)
        '''

        try:
            driver.get("https://www.linkedin.com/in/dhirajkelhe/" + "details/experience/")
            # WebDriverWait(driver, 10)
            time.sleep(4)
            soup = create_soup(driver.page_source)

            all_exp = soup.find_all('li', {'class', 'pvs-list__paged-list-item artdeco-list__item pvs-list__item--line-separated pvs-list__item--one-column'})

            def extract_exp_data(sample):
                role = sample.find('div', {'class', 'display-flex flex-wrap align-items-center full-height'}).text.strip()
                role = role[:len(role)//2]

                company_and_job_type = sample.find('span', {'class', 't-14 t-normal'}).text.strip()
                company_and_job_type = company_and_job_type[:len(company_and_job_type)//2].split(" · ")
                company = company_and_job_type[0]
                
                try:
                    job_type = company_and_job_type[1]
                except:
                    job_type = None
                try:
                    period, duration = sample.find('span', {'class', "pvs-entity__caption-wrapper"}).text.split(' · ')
                    period = period.split(" - ")
                    
                except:
                    # this is a special case when an employee has worked more than one positions in the same company
                    # used 'extend' instead of 'append' for this reason only
                    company = role
                    job_type = None

                    multiples = sample.find_all('li', {'class':'pvs-list__paged-list-item pvs-list__item--one-column'})

                    jobs = []
                    for x in multiples:
                        role = x.find('div', {'class', 'display-flex flex-wrap align-items-center full-height'}).text.strip()
                        role = role[:len(role)//2]
                        job_type = x.find('span', {'class':'t-14 t-normal'}).text.strip()
                        job_type = job_type[:len(job_type)//2]
                        
                        period, duration = x.find('span', {'class', "pvs-entity__caption-wrapper"}).text.split(' · ')
                        period = period.split(" - ")
                        if period[1] != 'Present':
                            period = {'from': datetime.strptime(period[0], "%b %Y"), 'to': datetime.strptime(period[1], "%b %Y")}
                        else:
                            period = {'from': datetime.strptime(period[0], "%b %Y"), 'to': datetime.strptime(datetime.now().strftime("%b %Y"), "%b %Y")}
                        
                        try:
                            duration = int(duration.split(" ")[0]) * 12 + int(duration.split(" ")[2])
                        except:
                            if duration.split(" ")[1] == 'yrs':
                                duration = int(duration.split(" ")[0]) * 12
                            else: duration = int(duration.split(" ")[0])
                        jobs.append({'role':role, 'company':company, 'job_type':job_type, 'from':period['from'], 'to':period['to'], 'duration':duration})
                    return jobs
                

                try:
                    duration = int(duration.split(" ")[0]) * 12 + int(duration.split(" ")[2])
                except:
                    if duration.split(" ")[0] == 'yrs':
                        duration = int(duration.split(" ")[0]) * 12
                    else: duration = int(duration.split(" ")[0])

                if period[1] != 'Present':
                    period = {'from': datetime.strptime(period[0], "%b %Y"), 'to': datetime.strptime(period[1], "%b %Y")}
                else:
                    period = {'from': datetime.strptime(period[0], "%b %Y"), 'to': datetime.strptime(datetime.now().strftime("%b %Y"), "%b %Y")}

                return [{'role':role, 'company':company, 'job_type':job_type, 'from':period['from'], 'to':period['to'], 'duration':duration}]

            all_experiences = []
            for i in  all_exp:
                all_experiences.extend(extract_exp_data(i))

            return all_experiences
        
        except Exception as error:
            logger.error(error)
            return self.get_experience()
    

    def get_education(self):
        '''
        For all edu: college, degree, from, to (list->dict)
        '''

        try:
            driver.get(self.profile_link + 'details/education/')
            # WebDriverWait(driver, 10)
            time.sleep(page_delay)
            soup = create_soup(driver.page_source)

            all_edu = soup.find_all('li', {'class', 'pvs-list__paged-list-item artdeco-list__item pvs-list__item--line-separated pvs-list__item--one-column'})

            def extract_education_data(sample):
                college = sample.find('div', {'class', 'display-flex flex-wrap align-items-center full-height'}).text.strip()
                college = college[:len(college)//2]
                degree = sample.find('span', {'class', 't-14 t-normal'}).text.strip()
                degree = degree[:len(degree)//2]
                try:
                    period = sample.find('span', {'class', 'pvs-entity__caption-wrapper'}).text.strip().split(" - ")
                    period = {'from': period[0], 'to': period[1]}
                except:
                    period = {'from': None, 'to': None}
                return {'college':college, 'degree':degree, 'from':period['from'], 'to':period['to']}

            all_education = []
            for i in  all_edu:
                all_education.append(extract_education_data(i))
            
            if all_education == []:
                logger.info("Education Section: could not load site on time")
                all_education = self.get_education()
            
            
            return all_education
        
        except Exception as error:
            logger.error(error)
            return self.get_education()
        

    def get_certifications(self):
        '''
        For all certs: name, org, issued, link (list->dict)
        '''
        try:
            driver.get(self.profile_link + 'details/certifications/')
            # WebDriverWait(driver, 10)
            time.sleep(page_delay)
            soup = create_soup(driver.page_source)

            def extract_certifications(sample):
                sample = all_certs[0]
                name = sample.find('div', {'class', 'display-flex flex-wrap align-items-center full-height'}).text.strip()
                organization = sample.find('span', {'class', 't-14 t-normal'}).text.strip()
                organization = organization[:len(organization)//2]
                try:
                    issued = datetime.strptime(sample.find('span', {'class', 'pvs-entity__caption-wrapper'}).text.split("Issued")[1].strip(), '%b %Y')
                except:
                    issued = None
                try:
                    link = sample.find('a', {'class', 'optional-action-target-wrapper artdeco-button artdeco-button--secondary artdeco-button--standard artdeco-button--2 artdeco-button--muted inline-flex justify-center align-self-flex-start button-placement-wrap'}).get('href')
                except:
                    link = None
                return {'cert_name':name, 'cert_org': organization, 'cert_issued':issued, 'cert_link':link}

            all_certs = soup.find_all('li', {'class', 'pvs-list__paged-list-item artdeco-list__item pvs-list__item--line-separated pvs-list__item--one-column'})

            all_certification = []
            for i in  all_certs:
                all_certification.append(extract_certifications(i))

            if all_certification == []:
                logger.info("Certification Section: could not load site on time")
                all_certification = self.get_certifications()
            

            return all_certification
        except Exception as error:
            logger.error(error)
            return self.get_certifications()

 
    def get_skills(self):
        '''
        Skills (list)
        '''

        try:
            driver.get(self.profile_link + 'details/skills/')
            # WebDriverWait(driver, 10)
            time.sleep(page_delay)
            soup = create_soup(driver.page_source)

            all_skills = soup.find_all('li', {'class', 'pvs-list__paged-list-item artdeco-list__item pvs-list__item--line-separated pvs-list__item--one-column'})

            def extract_skills(sample):
                '''
                skill
                '''
                skill = sample.find('div', {'class':"display-flex flex-wrap align-items-center full-height"}).text.strip()
                skill = skill[:len(skill)//2]
                return skill

            skills = set()
            for i in all_skills:
                skills.add(extract_skills(i))
            skills = list(skills)

            if skills == []:
                logger.info("Skills Section: could not load site on time")
                skills = self.get_skills()
            
            return skills
        except Exception as error:
            logger.error(error)
            return self.get_skills()
        
    
    def get_languages(self):
        '''
        For all languages: languages, profiency (list->dict)
        '''

        try:
            driver.get(self.profile_link + 'details/languages/')
            # wait = WebDriverWait(driver, 10)
            time.sleep(page_delay)
            soup = create_soup(driver.page_source)

            all_langs = soup.find_all('li', {'class', 'pvs-list__paged-list-item artdeco-list__item pvs-list__item--line-separated pvs-list__item--one-column'})

            def extract_langs(sample):
                lang = sample.find('div', {'class':"display-flex flex-wrap align-items-center full-height"}).text.strip()
                lang = lang[:len(lang)//2]
                profiency = sample.find('span', {'class':"t-14 t-normal t-black--light"}).text.strip()
                profiency = profiency[:len(profiency)//2]

                return {'language':lang, 'profiency':profiency}

            langs = []
            for i in all_langs:
                langs.append(extract_langs(i))
            
            if langs == []:
                logger.info("Language Section: could not load site on time")
                langs = self.get_languages()
            
            
            
            return langs
        except Exception as error:
            logger.error(error)
            return self.get_languages
    

    def get_awards(self):
        '''
        For all awards: award_name, org, date (list->dict)
        '''
        try:
            driver.get(self.profile_link + 'details/honors/')
            # wait = WebDriverWait(driver, 10)
            time.sleep(page_delay)
            soup = create_soup(driver.page_source)

            all_awards = soup.find_all('li', {'class', 'pvs-list__paged-list-item artdeco-list__item pvs-list__item--line-separated pvs-list__item--one-column'})

            def extract_awards(sample):

                award_name = sample.find('div', {'class':"display-flex flex-wrap align-items-center full-height"}).text.strip()
                award_name = award_name[:len(award_name)//2]
                try:
                    org_and_date = sample.find('span', {'class':"t-14 t-normal"}).text.strip()
                    org_and_date = org_and_date[:len(org_and_date)//2].split(' · ')
                    org = org_and_date[0]
                    try:
                        date = datetime.strptime(org_and_date[1], '%b %Y')
                    except:
                        date = None
                except:
                    org = date = None
                return {'award_name':award_name, 'org':org, 'date':date}


            awards = []
            for i in all_awards:
                awards.append(extract_awards(i))
            
            if awards == []:
                logger.info("Awards Section: could not load site on time")
                awards = self.get_awards()
            

            return awards
        except Exception as error:
            logger.error(error)
            return self.get_awards
        
    
    def get_all_the_data_my_slave(self):
        contact = self.get_contact_data()
        connections, followers, about = self.get_followers_and_about()
        
        try:
            if self.sections_available['experience']:
                experience = self.get_experience()
        except:
            experience = [{
                'role':None,
                'company': None,
                'job_type': None,
                'from': None,
                'to': None,
                'duration': None
            }]
        try:
            if self.sections_available['education']:
                education = self.get_education()
        except:
            education = [{
                'college': None,
                'degree': None,
                'from': None,
                'to': None
            }]
            

        try:
            if self.sections_available['licenses_and_certifications']:
                certification =  self.get_certifications()
        except:
            certification = [{
                'cert_name': None,
                'cert_org': None,
                'cert_issued': None,
                'cert_link': None
        }]

        try:
            if self.sections_available['skills']:
                skills = self.get_skills()
        except:
            skills = [None]

        try:
            if self.sections_available['languages']:
                languages = self.get_languages()
        except:
            languages = [{
                'language': None,
                'profiency': None
            }]
        try:
            if self.sections_available['honors_and_awards']:
                awards = self.get_awards()
        except:
            awards = [{
                'award_name': None,
                'org': None,
                'date': None
            }]


        return {
            'contact':contact,
            'connections':connections,
            'followers':followers,
            'about':about,
            'experience':experience,
            'education':education,
            'certification':certification,
            'skills':skills,
            'languages':languages,
            'awards':awards
        }