import os
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from pytube import YouTube
import instaloader
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import requests

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = '8012804738:AAEkIvfM03F3ZPtACdYtao1TunjhCZhpDik'

# YouTube API Key
YOUTUBE_API_KEY = 'AIzaSyCre0hFPuYyTkIq6bQpEcP4dE7SEDRsPlQ'

# Spotify API Credentials
SPOTIPY_CLIENT_ID = '828f2240b0a241f9871024c514d7b7be'
SPOTIPY_CLIENT_SECRET = '8fe5d7b55b864fbbb06b89ba3aa21d86'

# Initialize Spotify client
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET))

# Initialize Instaloader
L = instaloader.Instaloader()

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Welcome! Send me a link from Instagram, YouTube, or Spotify to download the media.')

def download_instagram(update: Update, context: CallbackContext, url: str) -> None:
    try:
        post = instaloader.Post.from_shortcode(L.context, url.split('/')[-2])
        L.download_post(post, target=f"{post.owner_username}_{post.shortcode}")
        update.message.reply_document(document=open(f"{post.owner_username}_{post.shortcode}/{post.date_utc.strftime('%Y-%m-%d_%H-%M-%S')}_UTC.jpg", 'rb'))
    except Exception as e:
        update.message.reply_text(f"Failed to download Instagram media: {e}")

def download_youtube(update: Update, context: CallbackContext, url: str) -> None:
    try:
        yt = YouTube(url)
        stream = yt.streams.filter(progressive=True, file_extension='mp4').first()
        stream.download(filename='video.mp4')
        update.message.reply_video(video=open('video.mp4', 'rb'))
    except Exception as e:
        update.message.reply_text(f"Failed to download YouTube video: {e}")

def download_spotify(update: Update, context: CallbackContext, url: str) -> None:
    try:
        track_id = url.split('/')[-1].split('?')[0]
        track = sp.track(track_id)
        preview_url = track['preview_url']
        if preview_url:
            response = requests.get(preview_url)
            with open('preview.mp3', 'wb') as f:
                f.write(response.content)
            update.message.reply_audio(audio=open('preview.mp3', 'rb'))
        else:
            update.message.reply_text("No preview available for this track.")
    except Exception as e:
        update.message.reply_text(f"Failed to download Spotify track: {e}")

def handle_message(update: Update, context: CallbackContext) -> None:
    url = update.message.text
    if 'instagram.com' in url:
        download_instagram(update, context, url)
    elif 'youtube.com' in url or 'youtu.be' in url:
        download_youtube(update, context, url)
    elif 'spotify.com' in url:
        download_spotify(update, context, url)
    else:
        update.message.reply_text("Unsupported URL. Please send a valid Instagram, YouTube, or Spotify link.")

def main() -> None:
    updater = Updater(TELEGRAM_BOT_TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()