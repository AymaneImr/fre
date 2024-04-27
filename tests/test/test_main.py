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
        username = url.split('https://www.')[1].rsplit('/')[1]
        #second method path = url.lstrip('https://www.')
        valid_url = 'https://www.instagram.com' 
        
        #the link should contains the correct instagram domain 
        #and at the same time it shouldn't be just the domain 
        #it should contains the account username at end of the url
        if url.startswith(valid_url) and url != valid_url:
            self.username = username
            return True
        else:
            raise Exception('Invalid instagram link')
    
    #get account by username
    def test_allowed_username(self, username=None, scrape=None):
        valid_url = 'https://www.instagram.com'
        
        #make sure that the user specified at least one argument
        if not username and not scrape :
            raise Exception('You forgot to pass one argument')
        elif username and len(username) <= 3 :
            raise Exception('invalid username!')
        elif scrape and len(scrape) <= 3:
            raise Exception('invalid username!')
        
        elif valid_url not in (username, scrape):
            
            #remove any spaces at the end to check for spaces in between
            if username:
                if username.endswith(' ') or username.startswith(' '):
                    username = username.rstrip(' ').lstrip(' ')
                    
                #check for any spaces left
                if ' ' not in username:
                    self.username = username
                    self.url = valid_url + '/' + self.username
                    return True
                return False
                
            elif scrape:
                if scrape.endswith(' ') or scrape.startswith(' '):
                    scrape = scrape.rstrip(' ').lstrip(' ')
                    
                #check for any spaces left
                if ' ' not in scrape:
                    self.scrape = scrape
                    return True
                return False
            
            return False
        
        return False
    
    #get instagram account url 
    def test_get_full_path(self, url):
        if self.test_allowed_url(url):
            self.url = url
            return True
        
        raise Exception('Something went wrong') 
    
    #get login information
    def test_login(self, username, password):
        if not self.test_allowed_username(username) or not password or len(password) <= 3:
            raise Exception('Either the password is not valid or username is not valid. please double check your information!')
        
        self.password = password
        return True


info = Info()

class Data(BaseCase):
    
    def setUp(self):
        super(Data, self).setUp()
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
        self.sleep(5)
        try:
            self.assert_text_not_visible('Sorry, your password was incorrect. Please double-check your password.')
        except Exception:
            raise Exception('The password is incorrect. Please double check your login information.')
        try:
            self.is_text_visible('Save your login info?', 'div')
        except Exception:
            raise Exception('Something went wrong.')
    
    #scrape data if logged in 
    def test_private(self, username, password, scrape):
        self.test_log_in(username, password)
        self.sleep(8)
        self.click('a:contains("Search")')
        self.sleep(8)
        info.test_allowed_username(scrape=scrape)
        self.type('input[placeholder="Search"]', info.scrape)
        self.sleep(6)
        self.click(f'a:contains("{info.scrape}")')
        self.sleep(7)
        self.test_scrape()
    
    def test_scrape(self):
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
                number = int(float(followers.rstrip('K').strip('.')) * 1000)
                return number
            return number
        
        self.followers = convert_number(followers)
        self.following = convert_number(following)
        
        #get the user profile pic url
        image_src = self.get_image_url(f'img[alt="{info.username}\'s profile picture"]')
        self.profile_pic_url = image_src
        
        #get the account name
        acc_name = self.find_element('.x7a106z span.x1lliihq')
        self.name = acc_name.text
        
        #get the bio
        try:
            bio = self.find_element('.x7a106z h1._ap3a')
            self.bio = bio.text
        except Exception:
            self.bio = None
            pass
        
        #account's information in excel file 
        self.test_get_acc_info()
        
        #check if account is private
        try: 
            self.assert_text_not_visible('This account is private')
        except Exception:
            raise Exception('The account you\'re trying to scrape is private you can\'t see his/her following/followers data.')
        
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
        
        #find the div in pop up that control the scrolling
        popup = self.find_element('._aano')
        if data_file == 'followers':
            scroll_times = int(self.followers) // 5
        else:
            scroll_times = int(self.following) // 5
        
        #scroll down inside the popup
        for i in range(scroll_times + 1):
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
        try:
            df = pd.DataFrame(data)
        except ValueError:
            df = pd.DataFrame.from_dict(data, orient='index')
        
        #convert dataframe into an excel file
        #generate followers file
        if data_file == 'followers':
            file = f'{info.scrape}followers.xlsx'
            followers_file = df.to_excel(file)
            return followers_file
        
        #generate following file
        elif data_file == 'following':
            file = f'{info.scrape}following.xlsx'
            following_file = df.to_excel(file)
            return following_file
    
    def test_get_acc_info(self):
        acc_info_data = {
            'username': info.scrape,
            'name': self.name,
            'url': f'https://www.instagram.com/{info.scrape}',
            'profile_pic_url': self.profile_pic_url,
            'posts': self.posts,
            'followers': self.followers,
            'following': self.following,
            'bio': self.bio
        }
        
        #generate dataframe store the acc available information
        df1 = pd.DataFrame(acc_info_data, index=[0])
        acc_info_name = f'{info.username}_info.xlsx'
        acc_info_file = df1.to_excel(acc_info_name)
        return acc_info_file
    
    #scrape public accounts without log in
    def test_public(self, url):
        info.test_get_full_path(url)
        self.open(info.url)
        self.sleep(6)
        
        #check if the url exist
        try:
            self.assert_text_not_visible("Sorry, this page isn't available.")
        except Exception:
            raise Exception('The link you followed may be broken, or the page may have been removed.')
        
        #check if the instagram give access without login
        try:
            self.assert_text_not_visible("Something went wrong")
        except Exception:
            raise Exception('Something went wrong please try again or just login to solve the problem')
        
        #check if account is private
        try: 
            self.assert_text_not_visible('This account is private')
        except Exception:
            raise Exception('The account you\'re trying to scrape is private')
        
        self.test_scrape()
    
    def test_start_scrape(self):
        keep_scraping = True
        print('\nWelcome to Instagram-bot followers/ing scraping.')
        print('Type stop/s/f if you would like to stop the program.')
        while keep_scraping:
            acc_type = input('Type private/pv/v for private account / public/pb/b for public account. \n').lower()
            
            if acc_type in ['pv', 'private']:
                username = input('Account\'s username: ')
                password = input('Account\'s password:  ')
                scrape   = input('Account to scrape: ')
                self.test_private( username=username, password=password, scrape=scrape)
            
            elif acc_type in ['pb', 'public']:
                url = input('Provide account\'s link: ')
                self.test_public(url)
            
            print('Type stop/s/f if you would like to stop the program.')
            
            #scrape again or stop the program
            to_continue = input('If you want to continue scraping click "ENTER". if not type stop/s/f ').lower()
            if to_continue in ['stop', 's', 'f']:
                keep_scraping = False