#!/bin/bash

# 🚀 سكربت التشغيل السريع لبوت TikTok Username Checker

echo "🎯 بدء إعداد بوت TikTok Username Checker..."

# التحقق من وجود Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 غير مثبت. يرجى تثبيته أولاً."
    exit 1
fi

echo "✅ تم العثور على Python"

# إنشاء البيئة الافتراضية إذا لم تكن موجودة
if [ ! -d "venv" ]; then
    echo "📦 إنشاء البيئة الافتراضية..."
    python3 -m venv venv
fi

# تفعيل البيئة الافتراضية
echo "🔄 تفعيل البيئة الافتراضية..."
source venv/bin/activate

# تثبيت المكتبات
echo "📚 تثبيت المكتبات المطلوبة..."
pip install -r requirements.txt

# التحقق من وجود التوكن
if [ -z "$BOT_TOKEN" ]; then
    echo "⚠️  متغير BOT_TOKEN غير مُعرّف"
    echo "📝 يرجى تعيين التوكن:"
    echo "   export BOT_TOKEN='8138519590:AAHOAhelbbtpOqCaCoKEPOW77Q1IbzgVytY'"
    echo ""
    read -p "🔑 أدخل توكن البوت الآن: " token
    export BOT_TOKEN="$token"
fi

# التحقق من صحة التوكن
if [[ ! $BOT_TOKEN =~ ^[0-9]+:[a-zA-Z0-9_-]+$ ]]; then
    echo "❌ التوكن غير صحيح. يجب أن يكون بالشكل: 123456789:ABCDefGhIJKLmnoPQRStuVWXyz"
    exit 1
fi

echo "✅ التوكن صحيح"

# تشغيل البوت
echo "🚀 تشغيل البوت..."
echo "📱 يمكنك الآن استخدام البوت على Telegram"
echo "🛑 اضغط Ctrl+C لإيقاف البوت"
echo ""

python3 bot.py