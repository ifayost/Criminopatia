import argparse
import eyed3
import json
import re
import requests

from bs4 import BeautifulSoup
from credentials import username, password
from pathlib import Path

eyed3.log.setLevel("ERROR")


# Folder Structure
SAVE_PATH = Path('./Criminopatia/')
if not SAVE_PATH.exists():
    SAVE_PATH.mkdir()
CF_PATH = SAVE_PATH / 'Club de Fans'
if not CF_PATH.exists():
    CF_PATH.mkdir()
EPISODES_PATH = SAVE_PATH / 'Episodios'
if not EPISODES_PATH.exists():
    EPISODES_PATH.mkdir()


headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
        }

exfat_illegal_chars = {
        # '"': "'",
        # '*': '',
        # '/': '.',
        # ':': '.',
        # '<': '_',
        # '>': '_',
        # '?': '¿',
        # '\\': '.',
        # '|': '.'
        }

json_decode = {
        '\\u0022': '"',
        '\\\\\\/': '/',
        }


def loggin(s, username, password):
    login_data = {
            'action': 'tve_login_submit',
            'after_submit': 'redirect',
            'username': username,
            'password': password,
            'remember_me': '',
            'custom_action': 'login'
            }
    _ = s.get('https://criminopatia.com/entrar/')
    _ = s.post('https://criminopatia.com/wp-admin/admin-ajax.php', data=login_data)
    return s


def set_metadata(mp3, title, image=None, image_type=None, track_num=None,
                 description=None):
    audiofile = eyed3.load(str(mp3))
    audiofile.initTag()
    audiofile.tag.artist = 'Criminopatia'
    audiofile.tag.album = title 
    audiofile.tag.title = title
    audiofile.tag.genere = 'True Crime'
    audiofile.tag.images.set(3, image, f'image/{image_type}')
    audiofile.tag.track_num = track_num
    audiofile.tag.description = description
    audiofile.tag.save()


def download_episode_cf(s, link, link_container, path):
    r = s.get(link)
    soup = BeautifulSoup(r.content.decode(), 'html.parser')
    title = soup.title.string.replace(' - Criminopatia', '')
    episode_path = title
    for k, v in exfat_illegal_chars.items():
        episode_path = episode_path.replace(k, v)
    print(f'\n[+] {title}: ', end=' ')
    episode_path = path / episode_path
    mp3_in_path = list(episode_path.glob('**/*.mp3'))
    if mp3_in_path:
        print('√', end='')
    else:
        print('Downloading... ', end=' ')
        if not episode_path.exists():
            episode_path.mkdir()
        download_link = [link.get('href') for link in soup.find_all('a')]
        download_link = [link for link in download_link if link is not None]
        download_link = [link for link in download_link
                         if ('api.spreaker.com' in link) & ('download' in link)]
        if download_link:
            episode_path.mkdir()
            image = link_container.find('img')
            src = image.get('srcset')
            if src is None:
                src = image.get('src')
            image = src.split(', ')[-1].split(' ')[0]
            image_name = image.split('/')[-1]
            r_image = s.get(image)
            # with (episode_path / image_name).open('wb') as f:
            #     f.write(r_image.content)
            for i, link in enumerate(download_link):
                r = s.get(link)
                filename = re.search(
                        r'filename="(.*?)"', r.headers['Content-Disposition']
                        ).group(1)
                with (episode_path / filename).open('wb') as f:
                    f.write(r.content)
                set_metadata(
                        mp3 = episode_path / filename,
                        title = title,
                        image = r_image.content,
                        image_type = image_name.split('.')[-1],
                        track_num = i + 1
                        )
                print('√', end='')
        else:
            print('\n[!] Download link not found.')


def scrape_club_de_fans(s):
    print('\n\n[*] SCRAPING GLUB DE FANS')
    r = s.get('https://criminopatia.com/club-de-fans/')
    soup = BeautifulSoup(r.content.decode(), 'html.parser')
    for article in soup.find_all('article'):
        link = article.find('a')
        link = link.get('href')
        download_episode_cf(s, link, article, CF_PATH)
    print('\n')


def scrape_archive(s):
    criminopatia = 'https://criminopatia.com/'
    filter_keywords = [
            '/episodios/', '/club-de-fans/', '/mi-cuenta/', '/faqs/', '/wp-login.php', 
            '/club-de-fans-archivo/', '/registro/'
            ]
    print('\n\n[*] SCRAPING ARCHIVE')
    r = s.get('https://criminopatia.com/club-de-fans-archivo/')
    soup = BeautifulSoup(r.content.decode(), 'html.parser')
    for Link in soup.find_all('a'):
        link = Link.get('href')
        filters = all([text not in link for text in filter_keywords])
        if (criminopatia in link) & filters & (link != criminopatia):
            download_episode_cf(s, link, Link, CF_PATH)
    print('\n')


def download_episode(s, article, link):
    description = None
    image = article.find(
            'style', class_='tcb-post-list-dynamic-style'
            ).text
    image = re.search(
            r'background-image: url\("(.*?)"\)', image
            ).group(1)
    image_type = image.split('.')[-1]
    image = s.get(image).content
    
    r = s.get(link)
    soup = BeautifulSoup(r.content.decode(), 'html.parser')
    iframe = soup.find_all('iframe')
    Spreaker = True
    if iframe:
        link = iframe[0].get('src')
        if link[:6] == 'https:':
            r = s.get(link)
            iframe_soup = BeautifulSoup(r.content.decode(), 'html.parser')
            scripts = iframe_soup.find_all('script')
            data = [script for script in scripts if script.get('id') == "__NEXT_DATA__"]
            if data:
                data = data[0].text
                data = json.loads(data)['props']['pageProps']
                if ('clip' in data.keys()):
                    description = data['clip']['Description']
                    audio_link = data['clip']['AudioUrl'] 
                    Spreaker = False
                elif ('state' in data.keys()):
                    data = data['state']['data']
                    audio_link = data['defaultAudioFileObject']['passthroughUrl']
                    Spreaker = False
    if Spreaker:
        link = soup.find('a', class_='spreaker-player').get('href')
        r = s.get(link)
        soup = BeautifulSoup(r.content.decode(), 'html.parser')
        audio_link = soup.find('div', class_='max-w-screen-2xl')
        audio_link = re.search(r"JSON.parse\('(.*?)'\)", audio_link.get('x-data')).group(1)
        for k, v in json_decode.items():
            audio_link = audio_link.replace(k, v)
        audio_link = json.loads(audio_link)['playback_url']
    r = s.get(audio_link)
    audio = r.content
    return audio, description, image, image_type


def scrape_episodes(s):
    print('\n\n[*] SCRAPING EPISODES')
    not_found = "It seems we can't find what you're looking for"
    with requests.Session() as s:
        s.headers.update(headers)
        r = s.get('https://criminopatia.com/episodios/')
        c = 1
        while not not_found in r.text: 
            print(f'\n\n[-] Page {c}')
            soup = BeautifulSoup(r.content.decode(), 'html.parser')
            articles = soup.find_all('article') 
            for article in articles:
                title = article.find('a', class_='tcb-article-cover-link') 
                number_match = re.match(r'^\d+\.\s', title.text) 
                if number_match:
                    episode_number = number_match[0].split('.')[0]
                    episode_path = title.text
                    for k, v in exfat_illegal_chars.items():
                        episode_path = episode_path.replace(k, v)
                    print(f'\n[+] {title.text}:', end=' ')
                    episode_path = EPISODES_PATH / episode_path
                    mp3_in_path = list(episode_path.glob('**/*.mp3'))
                    if mp3_in_path:
                        print('√', end='')
                        continue
                    else:
                        print('Downloading... ', end=' ')
                        if not episode_path.exists():
                            episode_path.mkdir()
                        link = title.get('href')
                        title = title.text
                        try:
                            audio, description, image, image_type = download_episode(s, article, link)
                            mp3_path = episode_path / f'{episode_path.name}.mp3'
                            with mp3_path.open('wb') as f:
                                f.write(audio)
                            set_metadata(
                                    mp3= mp3_path,
                                    title=title,
                                    image=image,
                                    image_type=image_type,
                                    track_num=episode_number,
                                    description=description
                                    )
                            print('√', end='')
                        except:
                            print('\n\n\t[!] Audio link not found.')
            c += 1 
            r = s.get(f'https://criminopatia.com/episodios/page/{c}/')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            prog='criminopatia',
            description='Scrapea y descarga todos los episodios de Criminopatía.',
            epilog= ('Si no se añade ninguna flag, por defecto scrapea y descarga' 
                     + ' los episodios y el club de fans.')
            )
    parser.add_argument('--episodes', action='store_true', 
                        help='Scrapea y descarga los episodios')
    parser.add_argument('--cf', action='store_true', 
                        help='Scrapea y descarga el contenido del club de fans')
    parser.add_argument('--archivo', action='store_true', 
                        help='Scrapea y descarga el contenido de los archivos')
    args = parser.parse_args()

    with requests.Session() as s:
        s.headers.update(headers)
        if any(vars(args).values()):
            if args.cf or args.archivo:
                s = loggin(s, username, password)
            if args.episodes:
                scrape_episodes(s)
            if args.cf:
                scrape_club_de_fans(s)
            if args.archivo:
                scrape_archive(s)
        else:
            s = loggin(s, username, password)
            scrape_episodes(s)
            scrape_club_de_fans(s)
