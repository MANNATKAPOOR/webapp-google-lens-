# Deployment Guide

This project is configured to deploy the Backend to **Render** via Docker and the Frontend to **Vercel** as a Flutter Web SPA. Both platforms offer generous free tiers suitable for this project.

## 1. Prerequisites
- A GitHub account.
- A [Render](https://render.com/) account.
- A [Vercel](https://vercel.com/) account.
- A Google Gemini API Key.

---

## 2. Push to GitHub
1. Create a new repository on GitHub.
2. Initialize git and push this project:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/ai-vision-ocr.git
   git push -u origin main
   ```

---

## 3. Deploy Backend (Render)
We use Render's native support for Docker and the `render.yaml` Blueprint.

1. Go to your Render Dashboard.
2. Click **New +** -> **Blueprint**.
3. Connect your GitHub repository.
4. Render will automatically detect the `render.yaml` file.
5. In the Render Dashboard, you will be prompted to enter the `GEMINI_API_KEY`. Paste your key.
6. Click **Apply**. Render will build and deploy the Docker image.
7. Note the URL of your backend (e.g., `https://ai-vision-backend.onrender.com`).

*Note: PaddleOCR models are large. The first build and cold starts on the free tier may take a few minutes.*

---

## 4. Deploy Frontend (Vercel)
Vercel is optimized for static sites and frontend frameworks. We have provided a `vercel.json` to handle SPA routing and security headers.

1. Go to your Vercel Dashboard.
2. Click **Add New** -> **Project**.
3. Import your GitHub repository.
4. In the Project Settings during import:
   - Framework Preset: `Other`
   - Root Directory: `frontend_flutter`
   - Build Command: `flutter build web --release`
   - Output Directory: `build/web`
5. Note: You may need to add a custom install command in Vercel to install Flutter if Vercel doesn't pre-install it:
   - Install Command: `git clone https://github.com/flutter/flutter.git -b stable && ./flutter/bin/flutter pub get`
6. Click **Deploy**.
7. Once deployed, note your frontend URL (e.g., `https://ai-vision-ocr.vercel.app`).

---

## 5. Local Sharing (Ngrok)
To quickly share your local version with someone nearby without deploying to the cloud:
1. Make sure your `FRONTEND_PATH` in `.env` is set to point to `frontend_flutter/build/web`.
2. Build the flutter web app: `cd frontend_flutter && flutter build web --release`
3. Start the backend server: `python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000`
4. Run ngrok: `ngrok http 8000`
5. Share the generated ngrok URL! The backend will automatically serve the flutter web app on the same URL.
