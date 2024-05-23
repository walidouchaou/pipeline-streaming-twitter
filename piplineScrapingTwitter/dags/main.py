
from loginTwitter import LoginTwitter

def main():
    # Create an instance of LoginTwitter
    twitter_login = LoginTwitter()
    data_line_twitter_page = twitter_login.get_twitter_hrefs()
    print(data_line_twitter_page)
    data = twitter_login.get_twitte(data_line_twitter_page)
    print(data)
if __name__ == "__main__":
    main()