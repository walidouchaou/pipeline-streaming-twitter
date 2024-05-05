
from loginTwitter import LoginTwitter

def main():
    # Create an instance of LoginTwitter
    twitter_login = LoginTwitter()
    twitter_login.login()
    twitter_login.open_web_site()
if __name__ == "__main__":
    main()