from seleniumbase import BaseCase
import pandas as pd

class Info:
    
    def __init__(self):
        self.username = str
        self.password = str
        self.scrape = str
        self.url = str
    
    #check if this is an instagram link
    def test_allowed_url(self, url):
        path = url.split('https://www.')[1]
        #second method path = url.lstrip('https://www.')
        valid_url = 'https://www.instagram.com' 
        
        #the link should contains the correct instagram domain 
        #and at the same time it shouldn't be just the domain 
        #it should contains the account username at end of the url
        if path.startswith('instagram.com') and url != valid_url:
            return True
        else:
            return False
    
    #get account by username
    def test_allowed_username(self, username=None, scrape=None):
        valid_url = 'https://www.instagram.com'
        
        #makesure that the user specified at least one argument
        if not username or len(username) <= 3 or not scrape or len(scrape) <= 3:
            raise Exception('You forgot to specify one argument')
            return False
        
        elif valid_url not in (username, scrape) :
            
            #remove any spaces at the end to check for spaces in between
            if username.endswith(' ') or username.startswith(' ') or scrape.endswith(' ') or scrape.startswith(' '):
                username = username.rstrip(' ').lstrip(' ')
                scrape = scrape.rstrip(' ').lstrip(' ')
                
                #check for any spaces left
                if ' ' not in (username, scrape):
                    self.username = username
                    self.scrape = scrape
                    self.url = valid_url + '/' + self.username
                    return True
                
                return False
            
            #if there are no spaces either at the start or at the end 
            else:
                if ' ' not in username:
                    self.username = username
                    self.scrape = scrape
                    self.url = valid_url + '/' + self.username
                    return True
                
                return False
            
        return False
    
    #get instagram account url 
    def test_get_full_path(self, url):
        if self.test_allowed_url(url):
            self.url = url
            return True
        
        return False
    
    #get login information
    def test_login(self, username, password):
        if not self.test_allowed_username(username) or not password or len(password) <= 3:
            raise Exception('Either the password is not valid or username is not valid. please double check your information!')
        
        self.password = password
        return True


info = Info()

class Data(BaseCase):
    
    def __init__(self):
        self.followers = int
        self.following = int
        self.posts = int
        self.username = info.username
        self.name = str
        self.profile_pic_url = str
        self.bio = str
        self.url = info.url
    
    def test_log_in(self, username, password):
        login_url = 'https://www.instagram.com/accounts/login'
        
        #open instagram login link 
        self.open(login_url)
        
        if not info.test_login(username, password):
            return False
        
        #login to instagram account
        self.type("input[name='username']", info.username)
        self.type("input[name='password']", info.password)
        self.click('button:contains("Log in")')
        
        if self.assert_exact_text("Sorry, this page isn't available."):
            raise Exception('The link you followed may be broken, or the page may have been removed.')
        
        #check for login status
        elif self.assert_exact_text("Sorry, your password was incorrect. Please double-check your password."):
            raise Exception('The password is incorrect. Please double check your login information.')
        if not self.assert_text('Save your login info?') and not self.assert_url('https://www.instagram.com/accounts/onetap/?next=/'):
            raise Exception('Something went wrong.')
    
    #scrape data if logged in 
    def test_private(self):
        self.test_log_in(info.username, info.password)
        self.sleep(8)
        self.click('a:contains("Search")')
        self.sleep(8)
        self.type('input[placeholder="Search"]', info.scrape)
        self.sleep(6)
        self.click(f'a:contains({info.scrape})')
        self.sleep(7)
        
        #check if account is private
        if self.assert_text('This account is private'):
            raise Exception('The account you\'re trying to scrape is private')
        
        #scraping followers, following and posts numbers
        numbers = self.find_elements('span[class="_ac2a"]')
        self.posts = numbers[0].text
        followers = numbers[1].text
        following = numbers[2].text
        
        #convert numbers form from (1K) to (1000)
        def convert_number(number):
            if 'M' in number:
                number = int(float(followers.rstrip('M').strip('.')) * 1000000)
                return number
            elif 'K' in number:
                number = int(float(followers.rstrip('M').strip('.')) * 1000)
                return number
            return number
        
        self.followers = convert_number(followers)
        self.following = convert_number(following)
        
        #get the user profile pic url
        image_src = self.get_image_url(f'img[alt="{info.scrape}\'s profile picture"]')
        self.profile_pic_url = image_src
        
        #get the account name
        acc_name = self.find_element('.x7a106z span.x1lliihq')
        self.name = acc_name
        
        #get the bio
        bio = self.find_element('.x7a106z h1._ap3a')
        self.bio = bio
        
        #following part 
        #click the following button to access the following data
        self.click('a:contains("following")')
        self.test_scrape_inside_popup('following')
        print('____________________________________________________')
        #click the return button to access the followers button
        self.click('polyline[stroke="currentColor"]')
        self.sleep(7)
        
        #followers part
        #click the followers button to access to followers data
        self.click('a:contains("followers")')
        self.test_scrape_inside_popup('followers')
    
    #scrape popup(following/followers) data
    def test_scrape_inside_popup(self, data_file):
        self.sleep(8)
        
        #scroll down inside the popup
        popup = self.find_element('._aano')
        for i in range(2):
            self.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", popup)
            self.sleep(2)
        
        #scrape following usernames and names and profile pic url
        usernames = self.find_elements('span._ap3a')
        usernames_data = []
        for username in usernames:
            #store usernames in a list 
            usernames_data.append(username.text)
        
        #scrape following names
        names = self.find_elements('._aano span.x1lliihq span.x6ikm8r')
        names_data = []
        for name in names:
            #store names in a list 
            names_data.append(name.text)
        
        #scrape following profile pic url and store it in a list
        img_elements_src = self.find_elements('.x1ja2u2z[role="dialog"] img[src]')
        sources = []
        for img in img_elements_src:
            src = img.get_attribute("src")
            sources.append(src)
        
        #scrape accounts url
        urls = self.find_elements('.x1ja2u2z[role="dialog"] .xdl72j9 .x9f619 .x1rg5ohu a.x4uap5[href]')
        url_acc = []
        for url in urls:
            urll = url.get_attribute("href")
            #store accounts url in a list 
            url_acc.append(urll)
        
        #formating data in a df
        data = {
            'username': usernames_data,
            'name': names_data,
            'url': url_acc,
            'pic_url': sources
        }
        
        #create a dataframe 
        df = pd.DataFrame(data)
        
        #convert dataframe into an excel file
        #generate followers file
        if data_file == 'followers':
            file = 'followers.xlsx'
            followers_file = df.to_excel(file)
            return followers_file
        
        #generate following file
        elif data_file == 'following':
            file = 'following.xlsx'
            following_file = df.to_excel(file)
            return following_file
    
    #scrape public accounts without log in
    def test_public(self):
        self.open(info.url)
        self.sleep(6)
        
        #check if account is private
        if self.assert_text('This account is private'):
            raise Exception('The account you\'re trying to scrape is private')
        
        #scraping followers, following and posts numbers
        numbers = self.find_elements('span[class="_ac2a"]')
        self.posts = numbers[0].text
        self.followers = numbers[1].text
        self.following = numbers[2].text
        
        #get the user profile pic url
        image_src = self.get_image_url(f'img[alt="{info.scrape}\'s profile picture"]')
        self.profile_pic_url = image_src
        
        #get the account name
        acc_name = self.find_element('.x7a106z span.x1lliihq')
        self.name = acc_name
        
        #get the bio
        bio = self.find_element('.x7a106z h1._ap3a')
        self.bio = bio
        
        #following part 
        #click the following button to access the following data
        self.click('a:contains("following")')
        self.test_scrape_inside_popup('following')
        print('____________________________________________________')
        #click the return button to access the followers button
        self.click('polyline[stroke="currentColor"]')
        self.sleep(7)
        
        #followers part
        #click the followers button to access to followers data
        self.click('a:contains("followers")')
        self.test_scrape_inside_popup('followers')