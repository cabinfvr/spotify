
# 🎧 spotify

display your current spotify listening status through a sleek web UI + simple API. built with spotipy, the spotify api, and flask

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/import/project?template=https://github.com/cabinfvr/spotify)


## 📸 examples

![screenshot 1](https://i.imgur.com/XKzPcDA.png)
![screenshot 2](https://i.imgur.com/piAaI4M.png)
![screenshot 3](https://i.imgur.com/WOncZ4y.png)

---

## 🧠 api reference

these endpoints return live spotify data from your current playback:

* `GET /api/title`
  👉 returns the current track title

* `GET /api/artist`
  👉 returns the current artist

* `GET /api/image`
  👉 returns the current album artwork

---

## 🚀 deploying with vercel tutorial

you can get all your spotify credentials from 👉 [spotify.dev](https://spotify.dev)
to generate a refresh token, go here 👉 [spotify-refresh-token-generator.netlify.app](https://spotify-refresh-token-generator.netlify.app/)

after you deploy, head to your **vercel dashboard**
👉 go to your project → **settings** → **environment variables**
add these:

```
SPOTIFY_USERNAME = your spotify username

SPOTIFY_REDIRECT_URI = https://spotify-refresh-token-generator.netlify.app/
# (can technically be anything valid, it’s not used in prod but required for token gen)

SPOTIFY_CLIENT_ID = your client id from spotify.dev

SPOTIFY_CLIENT_SECRET = your client secret from spotify.dev

SPOTIFY_REFRESH_TOKEN = your refresh token from spotify-refresh-token-generator.netlify.app
```

once that’s done, redeploy + boom 🎧🌈🎶

---

### spotify refresh token generator basic setup

![screenshot 4](https://i.imgur.com/9pnH2iH.png)

---

enjoy 🎵💻
