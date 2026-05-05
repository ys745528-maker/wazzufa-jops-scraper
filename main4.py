import requests 
from bs4 import BeautifulSoup
import csv
from itertools import zip_longest

jop_title = []
company_name = []
location_name = []
skills = []
links = []
salary = []
responsibilities = []
date = []
page_num = 0

print("Starting to scrape job list...")

while True:
    try:
        # الرابط الصحيح (تأكدي من المسافة قبل وبعد المتغيرات)
        url =f'https://wuzzuf.net/search/jobs?q=python2&start={page_num}'
        result = requests.get(url)
        source = result.content
        soup = BeautifulSoup(source, 'lxml')
        
        # تحديد عدد الصفحات (مثلاً أول 5 صفحات للتجربة السريعة)
        if page_num > 5: 
            print('Reached page limit.')
            break

        # إيجاد العناصر الأساسية
        jop_titles = soup.find_all('h2', {"class":"css-193uk2c"})
        company_names = soup.find_all('a', {'class':'css-ipsyv7'})
        locations_names = soup.find_all('span', {'class':'css-16x61xq'})
        jop_skills = soup.find_all('div', {'class':'css-1rhj4yg'})
        
        posted_new = soup.find_all('div', {'class':'css-eg55jf'})
        posted_old = soup.find_all('div', {'class':'css-1jldrig'})
        posted = [*posted_new, *posted_old]

        # إذا لم يجد وظائف في الصفحة يخرج من اللوب
        if not jop_titles:
            print("No more jobs found.")
            break

        for i in range(len(jop_titles)):
            jop_title.append(jop_titles[i].text.strip())
            
            # استخراج الرابط بشكل آمن
            link_tag = jop_titles[i].find('a')
            if link_tag:
                link = link_tag.attrs['href']
                if link.startswith('/'):
                    links.append('https://wuzzuf.net' + link)
                else:
                    links.append(link) 
            
            company_name.append(company_names[i].text.strip() if i < len(company_names) else "N/A")
            location_name.append(locations_names[i].text.strip() if i < len(locations_names) else "N/A")
            skills.append(jop_skills[i].text.strip() if i < len(jop_skills) else "N/A")
            
            # التاريخ
            date_val = posted[i].text.replace('-', '').strip() if i < len(posted) else "N/A"
            date.append(date_val)

        print(f'Page {page_num} processed.')
        page_num += 1
        
    except Exception as e:
        print(f'Error in main loop: {e}')
        break

# الدخول لكل رابط لسحب التفاصيل (الراتب والمتطلبات)
print(f"Fetching details for {len(links)} jobs. Please wait...")

for link in links:
    try:
        res = requests.get(link)
        src = res.content
        soup_detail = BeautifulSoup(src, 'lxml')
        
        # سحب الراتب باستخدام try/except بسيطة
        try:
            # هذا الكلاس يتغير أحياناً، نضع البديل "Confidential"
            sal = soup_detail.find('span', {'class': 'css-2rozun'})
            salary.append(sal.text.strip() if sal else "Confidential")
        except:
            salary.append("Confidential")

        # سحب المسؤوليات/المتطلبات
        try:
            req_div = soup_detail.find('div', {'class': 'css-1lqavbg'})
            if req_div and req_div.ul:
                items = [li.text.strip() for li in req_div.ul.find_all('li')]
                responsibilities.append(" / ".join(items))
            else:
                responsibilities.append("Not Specified")
        except:
            responsibilities.append("Not Specified")
            
    except:
        salary.append("Error fetching")
        responsibilities.append("Error fetching")

# حفظ الملف
file_list = [jop_title, company_name, date, location_name, skills, links, salary, responsibilities]
exported = zip_longest(*file_list)

try:
    with open('jopstest.csv', 'w', encoding='utf-8', newline='') as myfile:
        wr = csv.writer(myfile)
        wr.writerow(['Job Title', 'Company', 'Date', 'Location', 'Skills', 'Link', 'Salary', 'Responsibilities'])
        wr.writerows(exported)
    print("Success! File 'jopstest.csv' has been created.")
except Exception as e:
    print(f"Error saving CSV: {e}")
