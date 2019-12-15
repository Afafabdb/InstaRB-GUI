import os
from instapy import InstaPy
from instapy import smart_run
from instarb.models import UserToolSettings, UserInstagramAccounts 
from instarb import cipher_suite, app
from instapy import set_workspace
from instarb import url_extractor

def extract_url_from_text(content):
    url_list_to_like = []
    for url in url_extractor.gen_urls(content):
        url_list_to_like.append(url)
    return url_list_to_like


def instagram_password_decryption(insta_password):
    decoded_password = cipher_suite.decrypt(insta_password).decode('utf-8')
    return decoded_password

def run_instarb_auto_liker(user_id, insta_account_id, content):
    user_settings = UserToolSettings.query.filter_by(user_id=user_id).first()
    # headless_browser and live_broser opposite terms 
    headless_browser_value = False if user_settings.live_browser == 'True' else True 
    do_like_value = True if user_settings.do_like == 'True' else False
    like_randomize_value = True if user_settings.like_randomize == 'True' else False
    like_percentage_value = user_settings.like_percentage 

    user_insta_credentials = UserInstagramAccounts.query.filter_by(id=insta_account_id).first()
    insta_username = user_insta_credentials.insta_username
    insta_password = instagram_password_decryption(user_insta_credentials.insta_password)

    url_list_to_like = extract_url_from_text(content)
    
    user_workspace = os.path.join(app.root_path, 'workspace/')
    set_workspace(path=user_workspace)

    session = InstaPy(username=insta_username, password=insta_password, headless_browser=headless_browser_value, multi_logs=True)
    
    with smart_run(session, threaded=True):
        try:
            session.set_do_like(enabled=do_like_value, percentage=like_percentage_value)
            session.interact_by_URL(urls=url_list_to_like, randomize=like_randomize_value, interact=True)
            status = 'Success'
        except:
            print("CLOSED SESSION")
            status = 'Failed'
            session.end(threaded_session=True)

    return status


