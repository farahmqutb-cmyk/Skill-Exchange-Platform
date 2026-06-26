"""
email_notify.py — إرسال إشعارات البريد الإلكتروني لطلبات تبادل المهارات
يستخدم SMTP عبر Gmail
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# ══ إعدادات Gmail ══
# ضعي هنا بريدك الإلكتروني وApp Password بتاعتك
SMTP_EMAIL    = os.getenv("SMTP_EMAIL", "skillexchangehub2026@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "abcd efgh ijkl mnop")  # App Password من Google
SMTP_HOST     = "smtp.gmail.com"
SMTP_PORT     = 587


def send_email(to_email: str, subject: str, html_body: str) -> bool:
    """إرسال إيميل HTML"""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = f"Skill Exchange Hub <{SMTP_EMAIL}>"
        msg["To"]      = to_email

        msg.attach(MIMEText(html_body, "html", "utf-8"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.sendmail(SMTP_EMAIL, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"⚠️ Email error: {e}")
        return False


def notify_new_request(receiver_email: str, receiver_name: str,
                        sender_name: str, offered_skill: str,
                        wanted_skill: str, message: str,
                        request_id: int, site_url: str = "http://localhost:5000") -> bool:
    """
    إشعار المستلم بوجود طلب تبادل جديد
    يحتوي على زر قبول وزر رفض
    """
    accept_link = f"{site_url}/api/requests/{request_id}/accept_via_email?token=PLACEHOLDER"
    reject_link = f"{site_url}/api/requests/{request_id}/reject_via_email?token=PLACEHOLDER"

    html = f"""
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, sans-serif; background: #f5f5f5; margin: 0; padding: 20px; direction: rtl; }}
            .card {{ background: white; border-radius: 16px; max-width: 600px; margin: 0 auto; overflow: hidden; box-shadow: 0 10px 40px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, #B76E79, #D4AF37); padding: 40px; text-align: center; color: white; }}
            .header h1 {{ margin: 0; font-size: 1.8rem; }}
            .header p {{ margin: 8px 0 0; opacity: 0.9; }}
            .body {{ padding: 40px; }}
            .skill-box {{ background: #f8f3ff; border-radius: 12px; padding: 20px; margin: 20px 0; border-right: 4px solid #B76E79; }}
            .skill-box h3 {{ margin: 0 0 8px; color: #B76E79; }}
            .skill-box p {{ margin: 0; color: #555; font-size: 1.1rem; }}
            .message-box {{ background: #fff8f0; border-radius: 12px; padding: 20px; margin: 20px 0; font-style: italic; color: #666; border-right: 4px solid #D4AF37; }}
            .buttons {{ display: flex; gap: 15px; margin-top: 30px; justify-content: center; }}
            .btn-accept {{ background: linear-gradient(135deg, #4CAF50, #45a049); color: white; padding: 15px 40px; border-radius: 50px; text-decoration: none; font-weight: bold; font-size: 1.1rem; display: inline-block; }}
            .btn-reject {{ background: linear-gradient(135deg, #f44336, #d32f2f); color: white; padding: 15px 40px; border-radius: 50px; text-decoration: none; font-weight: bold; font-size: 1.1rem; display: inline-block; }}
            .footer {{ background: #f9f9f9; padding: 20px; text-align: center; color: #999; font-size: 0.9rem; }}
            .divider {{ border: none; border-top: 1px solid #eee; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <div class="card">
            <div class="header">
                <h1>⭐ Skill Exchange Hub</h1>
                <p>طلب تبادل مهارات جديد!</p>
            </div>
            <div class="body">
                <h2 style="color:#333;">مرحباً {receiver_name} 👋</h2>
                <p style="color:#555;font-size:1.1rem;">
                    لديك طلب تبادل مهارات جديد من <strong style="color:#B76E79;">{sender_name}</strong>
                </p>

                <div class="skill-box">
                    <h3>🎁 المهارة المعروضة</h3>
                    <p>{offered_skill}</p>
                </div>

                <div class="skill-box" style="border-right-color:#D4AF37;">
                    <h3>✨ المهارة المطلوبة</h3>
                    <p>{wanted_skill}</p>
                </div>

                {"<div class='message-box'><strong>رسالة من " + sender_name + ":</strong><br>" + message + "</div>" if message else ""}

                <hr class="divider">
                <p style="text-align:center;color:#666;">يرجى الرد على هذا الطلب:</p>
                <div class="buttons">
                    <a href="{accept_link}" class="btn-accept">✅ قبول الطلب</a>
                    <a href="{reject_link}" class="btn-reject">❌ رفض الطلب</a>
                </div>
                <p style="text-align:center;color:#999;font-size:0.85rem;margin-top:20px;">
                    أو يمكنك الرد من خلال الموقع مباشرةً من قسم لوحة التحكم
                </p>
            </div>
            <div class="footer">
                © 2025 Skill Exchange Hub — منصة تبادل المهارات
            </div>
        </div>
    </body>
    </html>
    """

    subject = f"⭐ طلب تبادل مهارة جديد من {sender_name} | Skill Exchange Hub"
    return send_email(receiver_email, subject, html)


def notify_request_accepted(sender_email: str, sender_name: str,
                             receiver_name: str, offered_skill: str,
                             wanted_skill: str) -> bool:
    """إشعار صاحب الطلب بأن طلبه تم قبوله"""
    html = f"""
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, sans-serif; background: #f5f5f5; margin: 0; padding: 20px; direction: rtl; }}
            .card {{ background: white; border-radius: 16px; max-width: 600px; margin: 0 auto; overflow: hidden; box-shadow: 0 10px 40px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, #4CAF50, #45a049); padding: 40px; text-align: center; color: white; }}
            .body {{ padding: 40px; }}
            .skill-box {{ background: #f0fff4; border-radius: 12px; padding: 20px; margin: 20px 0; border-right: 4px solid #4CAF50; }}
            .footer {{ background: #f9f9f9; padding: 20px; text-align: center; color: #999; font-size: 0.9rem; }}
        </style>
    </head>
    <body>
        <div class="card">
            <div class="header">
                <h1>🎉 تم قبول طلبك!</h1>
            </div>
            <div class="body">
                <h2>مرحباً {sender_name} 🌟</h2>
                <p style="font-size:1.1rem;color:#555;">
                    قام <strong style="color:#4CAF50;">{receiver_name}</strong> بقبول طلب تبادل المهارات الخاص بك!
                </p>
                <div class="skill-box">
                    <p>📚 <strong>{offered_skill}</strong> ↔ <strong>{wanted_skill}</strong></p>
                </div>
                <p>تواصل الآن مع {receiver_name} لترتيب موعد الجلسة الأولى 📅</p>
            </div>
            <div class="footer">© 2025 Skill Exchange Hub</div>
        </div>
    </body>
    </html>
    """
    subject = f"🎉 {receiver_name} قبل طلبك! | Skill Exchange Hub"
    return send_email(sender_email, subject, html)


def notify_request_rejected(sender_email: str, sender_name: str,
                             receiver_name: str) -> bool:
    """إشعار صاحب الطلب بأن طلبه تم رفضه"""
    html = f"""
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, sans-serif; background: #f5f5f5; margin: 0; padding: 20px; direction: rtl; }}
            .card {{ background: white; border-radius: 16px; max-width: 600px; margin: 0 auto; overflow: hidden; box-shadow: 0 10px 40px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, #9E9E9E, #757575); padding: 40px; text-align: center; color: white; }}
            .body {{ padding: 40px; }}
            .footer {{ background: #f9f9f9; padding: 20px; text-align: center; color: #999; font-size: 0.9rem; }}
        </style>
    </head>
    <body>
        <div class="card">
            <div class="header">
                <h1>طلبك لم يُقبل هذه المرة</h1>
            </div>
            <div class="body">
                <h2>مرحباً {sender_name}</h2>
                <p style="font-size:1.1rem;color:#555;">
                    للأسف، قام {receiver_name} بعدم قبول طلب التبادل هذه المرة.
                </p>
                <p style="color:#777;">لا تقلق! يوجد الكثير من الأعضاء الذين قد يهتمون بتبادل المهارات معك 🌟</p>
            </div>
            <div class="footer">© 2025 Skill Exchange Hub</div>
        </div>
    </body>
    </html>
    """
    subject = f"بخصوص طلب التبادل الخاص بك | Skill Exchange Hub"
    return send_email(sender_email, subject, html)
