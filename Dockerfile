# পাইথনের একটি স্থিতিশীল ভার্সন ব্যবহার করা হচ্ছে
FROM python:3.11.7-slim

# প্রয়োজনীয় সিস্টেম প্যাকেজ ইনস্টল করা হচ্ছে
RUN apt-get update && apt-get install -y --no-install-recommends git curl && \
    rm -rf /var/lib/apt/lists/*

# কাজের ডিরেক্টরি সেট করা হচ্ছে
WORKDIR /app

# requirements.txt ফাইলটি কপি করা হচ্ছে
COPY requirements.txt .

# --- প্রধান পরিবর্তনটি এখানে ---
# pip ক্যাশ পরিষ্কার করে এবং requirements.txt থেকে লাইব্রেরি ইনস্টল করা হচ্ছে
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# বাকি অ্যাপ্লিকেশন কোড কপি করা হচ্ছে
COPY . .

# বট চালানোর জন্য কমান্ড
CMD ["python3", "bot.py"]
