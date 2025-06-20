import asyncio
import logging
import re
import aiohttp
import json
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler, CallbackQueryHandler
from telegram.constants import ParseMode
import os

# إعداد نظام التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TikTokBot:
    def __init__(self, token):
        self.token = token
        self.user_stats = {}  # تتبع إحصائيات المستخدمين
        self.total_checks = 0
        self.ad_counter = 0
        self.ad_frequency = 3  # عرض إعلان كل 3 رسائل
        
        # إعدادات الإعلانات والتسويق (يمكنك تخصيصها)
        self.ads = [
            {
                "text": "🎯 هل تريد المزيد من الأدوات المفيدة؟ تابعنا للحصول على آخر التحديثات!",
                "url": "https://t.me/SaudiGamerz"  # ضع رابط قناتك هنا
            },
            {
                "text": "💎 احصل على خدمات تسويقية احترافية بأفضل الأسعار!",
                "url": "https://example.com"  # ضع رابط موقعك هنا
            },
            {
                "text": "🔥 انضم لمجتمعنا واحصل على أدوات حصرية!",
                "url": "https://t.me/SaudiGamerz"  # ضع رابط مجموعتك هنا
            }
        ]
        
        # رؤوس HTTP للطلبات
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

    async def check_tiktok_username(self, username):
        """فحص إتاحة اسم المستخدم على TikTok"""
        try:
            # تنظيف اسم المستخدم من الرموز الزائدة
            clean_username = re.sub(r'[^a-zA-Z0-9._]', '', username.replace('@', ''))
            
            if not clean_username:
                return False, "اسم المستخدم غير صالح"
            
            # التحقق من طول اسم المستخدم
            if len(clean_username) < 2 or len(clean_username) > 24:
                return False, "اسم المستخدم يجب أن يكون بين 2-24 حرف"
            
            url = f"https://www.tiktok.com/@{clean_username}"
            
            async with aiohttp.ClientSession(headers=self.headers, timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(url) as response:
                    if response.status == 404:
                        return True, "الاسم متاح ✅"
                    elif response.status == 200:
                        return False, "الاسم غير متاح ❌"
                    else:
                        return None, f"خطأ في الاتصال (كود: {response.status})"
                        
        except asyncio.TimeoutError:
            return None, "انتهت مهلة الاتصال، يرجى المحاولة مرة أخرى"
        except Exception as e:
            logger.error(f"خطأ في فحص اسم المستخدم {username}: {str(e)}")
            return None, "حدث خطأ أثناء الفحص، يرجى المحاولة مرة أخرى"

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر /start"""
        user = update.effective_user
        welcome_message = f"""
🎉 مرحباً {user.first_name}!

🔍 أنا بوت فحص أسماء المستخدمين على TikTok
✨ أرسل لي أي اسم مستخدم وسأتحقق من توفره فوراً!

📝 أمثلة على الاستخدام:
• ahmed123
• @cool_user
• user_name

🚀 ابدأ بإرسال اسم المستخدم الذي تريد فحصه!
        """
        
        keyboard = [
            [InlineKeyboardButton("📊 الإحصائيات", callback_data="stats")],
            [InlineKeyboardButton("ℹ️ المساعدة", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            welcome_message,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر /help"""
        help_text = """
🔍 <b>كيفية استخدام البوت:</b>

1️⃣ أرسل اسم المستخدم الذي تريد فحصه
2️⃣ انتظر النتيجة (متاح ✅ أو غير متاح ❌)
3️⃣ يمكنك فحص أسماء متعددة متتالية

📋 <b>قواعد أسماء المستخدمين:</b>
• يجب أن يكون بين 2-24 حرف
• يمكن أن يحتوي على حروف وأرقام و . و _
• لا يمكن أن يبدأ أو ينتهي بنقطة

⚡ <b>الأوامر المتاحة:</b>
/start - بدء البوت
/help - عرض المساعدة
/stats - عرض الإحصائيات

💡 <b>نصائح:</b>
• يمكنك إرسال الاسم مع أو بدون @
• البوت يدعم الأسماء بالعربية والإنجليزية
        """
        
        await update.message.reply_text(help_text, parse_mode=ParseMode.HTML)

    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر /stats"""
        user_id = update.effective_user.id
        user_checks = self.user_stats.get(user_id, 0)
        
        stats_text = f"""
📊 <b>إحصائيات البوت:</b>

👤 عمليات الفحص الخاصة بك: {user_checks}
🌍 إجمالي عمليات الفحص: {self.total_checks}
🕐 وقت التشغيل: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🎯 شكراً لاستخدامك البوت!
        """
        
        await update.message.reply_text(stats_text, parse_mode=ParseMode.HTML)

    def should_show_ad(self):
        """تحديد ما إذا كان يجب عرض إعلان"""
        self.ad_counter += 1
        return self.ad_counter % self.ad_frequency == 0

    def get_random_ad(self):
        """الحصول على إعلان عشوائي"""
        import random
        return random.choice(self.ads)

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج الرسائل النصية"""
        user_id = update.effective_user.id
        username = update.message.text.strip()
        
        # إرسال رسالة انتظار
        waiting_msg = await update.message.reply_text("🔍 جاري فحص الاسم، انتظر قليلاً...")
        
        try:
            # فحص اسم المستخدم
            is_available, message = await self.check_tiktok_username(username)
            
            # تحديث الإحصائيات
            self.total_checks += 1
            self.user_stats[user_id] = self.user_stats.get(user_id, 0) + 1
            
            # إنشاء الرد
            if is_available is True:
                emoji = "✅"
                status = "متاح"
                color = "🟢"
            elif is_available is False:
                emoji = "❌"
                status = "غير متاح"
                color = "🔴"
            else:
                emoji = "⚠️"
                status = "خطأ"
                color = "🟡"
            
            response_text = f"""
{color} <b>نتيجة الفحص:</b>

👤 اسم المستخدم: <code>{username}</code>
📱 المنصة: TikTok
🎯 الحالة: {message}

🔗 الرابط: https://www.tiktok.com/@{username.replace('@', '')}
            """
            
            # إنشاء لوحة المفاتيح
            keyboard = [
                [InlineKeyboardButton("🔍 فحص اسم آخر", callback_data="check_another")],
                [InlineKeyboardButton("📊 الإحصائيات", callback_data="stats")]
            ]
            
            # إضافة إعلان إذا لزم الأمر
            ad_text = ""
            if self.should_show_ad():
                ad = self.get_random_ad()
                ad_text = f"\n\n📢 <i>{ad['text']}</i>"
                keyboard.append([InlineKeyboardButton("🎯 اعرف المزيد", url=ad['url'])])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # حذف رسالة الانتظار وإرسال النتيجة
            await waiting_msg.delete()
            await update.message.reply_text(
                response_text + ad_text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.HTML
            )
            
        except Exception as e:
            logger.error(f"خطأ في معالجة الرسالة: {str(e)}")
            await waiting_msg.edit_text("❌ حدث خطأ أثناء معالجة طلبك، يرجى المحاولة مرة أخرى")

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أزرار الكيبورد المضمنة"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "stats":
            user_id = query.from_user.id
            user_checks = self.user_stats.get(user_id, 0)
            
            stats_text = f"""
📊 <b>إحصائيات البوت:</b>

👤 عمليات الفحص الخاصة بك: {user_checks}
🌍 إجمالي عمليات الفحص: {self.total_checks}
🕐 وقت التشغيل: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🎯 شكراً لاستخدامك البوت!
            """
            
            await query.edit_message_text(stats_text, parse_mode=ParseMode.HTML)
            
        elif query.data == "help":
            help_text = """
🔍 <b>كيفية استخدام البوت:</b>

1️⃣ أرسل اسم المستخدم الذي تريد فحصه
2️⃣ انتظر النتيجة (متاح ✅ أو غير متاح ❌)
3️⃣ يمكنك فحص أسماء متعددة متتالية

📋 <b>قواعد أسماء المستخدمين:</b>
• يجب أن يكون بين 2-24 حرف
• يمكن أن يحتوي على حروف وأرقام و . و _
• لا يمكن أن يبدأ أو ينتهي بنقطة

⚡ <b>الأوامر المتاحة:</b>
/start - بدء البوت
/help - عرض المساعدة
/stats - عرض الإحصائيات

💡 <b>نصائح:</b>
• يمكنك إرسال الاسم مع أو بدون @
• البوت يدعم الأسماء بالعربية والإنجليزية
            """
            await query.edit_message_text(help_text, parse_mode=ParseMode.HTML)
            
        elif query.data == "check_another":
            await query.edit_message_text("🔍 أرسل اسم المستخدم الجديد الذي تريد فحصه!")

    def run(self):
        """تشغيل البوت"""
        # إنشاء التطبيق
        application = Application.builder().token(self.token).build()
        
        # إضافة المعالجات
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("stats", self.stats_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # تشغيل البوت
        logger.info("🚀 تم تشغيل البوت بنجاح!")
        application.run_polling()

def main():
    """الدالة الرئيسية"""
    # الحصول على التوكن من متغير البيئة
    token = "8138519590:AAHOAhelbbtpOqCaCoKEPOW77Q1IbzgVytY"
    
    if not token:
        print("❌ يرجى تعيين متغير BOT_TOKEN")
        print("مثال: export BOT_TOKEN='your_bot_token_here'")
        return
    
    # إنشاء وتشغيل البوت
    bot = TikTokBot(token)
    bot.run()

if __name__ == "__main__":
    main()