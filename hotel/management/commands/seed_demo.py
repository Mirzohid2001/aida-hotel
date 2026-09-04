import io
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from PIL import Image, ImageDraw, ImageFont

from hotel.models import (
    AboutSection,
    Amenity,
    BlockedDate,
    Booking,
    FAQ,
    GalleryImage,
    HeroSlide,
    NearbyPlace,
    PolicyPage,
    Promotion,
    Room,
    RoomImage,
    RoomType,
    SeasonalPrice,
    SiteSettings,
    StatHighlight,
    Testimonial,
)
from hotel.services.booking import create_booking


def make_placeholder(name: str, size=(1600, 900), bg=(26, 22, 16), accent=(201, 160, 102), label="Aida") -> ContentFile:
    img = Image.new("RGB", size, bg)
    draw = ImageDraw.Draw(img)
    margin = size[0] // 8
    draw.rectangle([margin, margin, size[0] - margin, size[1] - margin], outline=accent, width=4)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Georgia.ttf", size=72)
    except OSError:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), label, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((size[0] - tw) / 2, (size[1] - th) / 2), label, fill=accent, font=font)
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=85)
    buffer.seek(0)
    return ContentFile(buffer.read(), name=name)


def set_i18n(obj, field: str, uz: str, ru: str, en: str) -> None:
    setattr(obj, field, uz)
    setattr(obj, f"{field}_uz", uz)
    setattr(obj, f"{field}_ru", ru)
    setattr(obj, f"{field}_en", en)


class Command(BaseCommand):
    help = "Seed rich demo content for Aida Hotel (UZ/RU/EN)"

    def handle(self, *args, **options):
        self._site_settings()
        self._about()
        self._hero_slides()
        self._stats()
        self._amenities()
        self._gallery()
        self._testimonials()
        self._faqs()
        self._promotion()
        self._nearby()
        self._policies()
        room_types = self._rooms()
        self._seasonal_prices(room_types)
        self._sample_bookings(room_types)
        self.stdout.write(self.style.SUCCESS("Database filled with rich demo content."))

    def _site_settings(self):
        s = SiteSettings.load()
        set_i18n(s, "site_name", "Aida Hotel", "Aida Hotel", "Aida Hotel")
        set_i18n(
            s,
            "tagline",
            "Buxoro markazidagi hashamatli dam olish",
            "Роскошный отдых в сердце Бухары",
            "Luxury stay in the heart of Bukhara",
        )
        s.phone = "+998 65 123 45 67"
        s.email = "info@aidahotel.uz"
        set_i18n(
            s,
            "address",
            "Aida Hotel, Buxoro sh., O'zbekiston",
            "Aida Hotel, г. Бухара, Узбекистан",
            "Aida Hotel, Bukhara, Uzbekistan",
        )
        s.check_in_time = "14:00"
        s.check_out_time = "12:00"
        s.map_latitude = Decimal("39.771356")
        s.map_longitude = Decimal("64.417423")
        s.facebook_url = "https://facebook.com/aidahotel"
        s.instagram_url = "https://instagram.com/aidahotel"
        s.telegram_url = "https://t.me/aidahotel"
        set_i18n(
            s,
            "meta_title",
            "Aida Hotel Buxoro — boutique mehmonxona | Bron qiling",
            "Aida Hotel Бухара — бутик-отель в центре | Забронировать",
            "Aida Hotel Bukhara — Boutique Hotel | Book Direct",
        )
        set_i18n(
            s,
            "meta_description",
            "Aida Hotel — Buxoro tarixiy markazidagi boutique mehmonxona. Qulay xonalar, hovli muhiti. Onlayn bron.",
            "Aida Hotel — бутик-отель в историческом центре Бухары. Комфортные номера, атмосфера дворика. Онлайн-бронирование.",
            "Aida Hotel — boutique hotel in historic Bukhara. Comfortable rooms, courtyard atmosphere. Book online.",
        )
        s.save()
        self.stdout.write("  Site settings")

    def _about(self):
        a = AboutSection.load()
        set_i18n(
            a,
            "title",
            "Aida Hotelga xush kelibsiz",
            "Добро пожаловать в Aida Hotel",
            "Welcome to Aida Hotel",
        )
        set_i18n(
            a,
            "content",
            "Aida Hotel — bu zamonaviy qulaylik va Sharqona mehmondo'stlik uyg'unligi. "
            "Eski shahar va Lyabi-Hauz maydoniga yaqin joylashgan mehmonxonamiz "
            "sayohatchilar va biznes mehmonlari uchun ideal tanlov.",
            "Aida Hotel — это сочетание современного комфорта и восточного гостеприимства. "
            "Наш отель расположен рядом с историческим центром и ансамблем Ляби-Хауз и идеально "
            "подходит для туристов и деловых гостей.",
            "Aida Hotel blends modern comfort with Eastern hospitality. "
            "Located near the historic center and Lyabi-Hauz, our hotel is ideal "
            "for travelers and business guests alike.",
        )
        a.image.save("about.jpg", make_placeholder("about.jpg", label="About Aida"), save=True)
        self.stdout.write("  About section")

    def _hero_slides(self):
        HeroSlide.objects.all().delete()
        slides = [
            {
                "uz": ("Aida Hotel", "Buxoroning yuragi", "Bron qilish"),
                "ru": ("Aida Hotel", "Сердце Бухары", "Забронировать"),
                "en": ("Aida Hotel", "Heart of Bukhara", "Book Now"),
                "url": "/book/",
                "color": (20, 18, 16),
            },
            {
                "uz": ("Hashamatli xonalar", "Har bir tafsilot siz uchun", "Xonalarni ko'rish"),
                "ru": ("Роскошные номера", "Каждая деталь для вас", "Номера"),
                "en": ("Elegant Rooms", "Every detail for you", "View Rooms"),
                "url": "/rooms/",
                "color": (42, 34, 26),
            },
            {
                "uz": ("Mukammal dam olish", "Terrasa, restoran va hovli", "Batafsil"),
                "ru": ("Идеальный отдых", "Терраса, ресторан и двор", "Подробнее"),
                "en": ("Perfect Relaxation", "Terrace, restaurant & courtyard", "Learn More"),
                "url": "/#amenities",
                "color": (61, 46, 32),
            },
        ]
        for i, slide_data in enumerate(slides, 1):
            slide = HeroSlide(ordering=i, cta_url=slide_data["url"], is_active=(i == 1))
            slide.title = slide_data["uz"][0]
            slide.title_uz = slide_data["uz"][0]
            slide.title_ru = slide_data["ru"][0]
            slide.title_en = slide_data["en"][0]
            slide.subtitle = slide_data["uz"][1]
            slide.subtitle_uz = slide_data["uz"][1]
            slide.subtitle_ru = slide_data["ru"][1]
            slide.subtitle_en = slide_data["en"][1]
            slide.cta_text = slide_data["uz"][2]
            slide.cta_text_uz = slide_data["uz"][2]
            slide.cta_text_ru = slide_data["ru"][2]
            slide.cta_text_en = slide_data["en"][2]
            if i == 1:
                hero_path = Path(settings.BASE_DIR) / "static" / "images" / "hero" / "aida-courtyard.png"
                with hero_path.open("rb") as hero_file:
                    slide.image.save(
                        "aida-courtyard.jpg",
                        ContentFile(hero_file.read()),
                        save=True,
                    )
            else:
                slide.image.save(
                    f"hero_{i}.jpg",
                    make_placeholder(f"hero_{i}.jpg", bg=slide_data["color"], label=slide_data["uz"][0]),
                    save=True,
                )
        self.stdout.write("  Hero slides (3)")

    def _stats(self):
        StatHighlight.objects.all().delete()
        data = [
            ("20", "Xonalar", "Номеров", "Rooms"),
            ("4.9", "Mehmon reytingi", "Рейтинг гостей", "Guest Rating"),
            ("24/7", "Konsyerj xizmati", "Консьерж 24/7", "Concierge"),
            ("5 min", "Lyabi-Hauzgacha", "До Ляби-Хауз", "To Lyabi-Hauz"),
        ]
        for i, (val, uz, ru, en) in enumerate(data, 1):
            s = StatHighlight(value=val, ordering=i, is_active=True)
            set_i18n(s, "label", uz, ru, en)
            s.save()
        self.stdout.write("  Stats (4)")

    def _amenities(self):
        Amenity.objects.all().delete()
        items = [
            (
                "Bepul Wi-Fi",
                "Tezkor internet butun mehmonxonada",
                "Бесплатный Wi-Fi",
                "Высокоскоростной интернет по всему отелю",
                "Free Wi-Fi",
                "High-speed internet throughout the hotel",
                "wifi",
            ),
            (
                "Nonushta",
                "Yevropa va milliy taomlar",
                "Завтрак",
                "Европейская и национальная кухня",
                "Breakfast",
                "European and local cuisine",
                "coffee",
            ),
            (
                "Terrasa",
                "Dam olish va choy uchun ochiq terrasa",
                "Терраса",
                "Открытая терраса для отдыха и чая",
                "Terrace",
                "Open terrace for rest and tea",
                "terrace",
            ),
            (
                "Hovli",
                "An'anaviy Buxoro hovlisi",
                "Внутренний двор",
                "Традиционный бухарский внутренний двор",
                "Courtyard",
                "Traditional Bukhara courtyard",
                "courtyard",
            ),
            (
                "Avtoturargoh",
                "Xavfsiz bepul parking",
                "Парковка",
                "Бесплатная охраняемая парковка",
                "Parking",
                "Secure complimentary parking",
                "parking",
            ),
            (
                "Restoran",
                "Milliy va xalqaro oshxona",
                "Ресторан",
                "Национальная и международная кухня",
                "Restaurant",
                "National and international cuisine",
                "restaurant",
            ),
            (
                "Transfer",
                "Aeroport va vokzal xizmati",
                "Трансфер",
                "Трансфер из аэропорта и вокзала",
                "Transfer",
                "Airport and railway station transfer",
                "car",
            ),
            (
                "24/7 Resepsiya",
                "Doimiy qabulxona xizmati",
                "Круглосуточная стойка",
                "Круглосуточное обслуживание",
                "24/7 Reception",
                "Round-the-clock front desk service",
                "clock",
            ),
        ]
        for i, (uz_n, uz_d, ru_n, ru_d, en_n, en_d, icon) in enumerate(items, 1):
            a = Amenity(icon=icon, ordering=i, is_active=True)
            set_i18n(a, "name", uz_n, ru_n, en_n)
            set_i18n(a, "description", uz_d, ru_d, en_d)
            a.save()
        self.stdout.write("  Amenities (8)")

    def _gallery(self):
        GalleryImage.objects.all().delete()
        items = [
            ("Lobbisi", "Лобби", "Lobby"),
            ("Syyut", "Люкс", "Suite"),
            ("Restoran", "Ресторан", "Restaurant"),
            ("Terrasa", "Терраса", "Terrace"),
            ("Hovli", "Внутренний двор", "Courtyard"),
            ("Eski shahar manzarasi", "Вид на старый город", "Old City View"),
            ("Deluxe xona", "Делюкс номер", "Deluxe Room"),
            ("Terrasa", "Терраса", "Terrace"),
        ]
        colors = [(20, 18, 16), (42, 34, 26), (61, 46, 32), (35, 28, 22)] * 2
        for i, (item, color) in enumerate(zip(items, colors), 1):
            uz_t, ru_t, en_t = item[0], item[1], item[2]
            gi = GalleryImage(ordering=i, is_active=True)
            set_i18n(gi, "title", uz_t, ru_t, en_t)
            set_i18n(gi, "caption", f"Aida Hotel — {uz_t}", f"Aida Hotel — {ru_t}", f"Aida Hotel — {en_t}")
            gi.image.save(f"gallery_{i}.jpg", make_placeholder(f"gallery_{i}.jpg", bg=color, label=uz_t), save=True)
        self.stdout.write("  Gallery (8)")

    def _testimonials(self):
        Testimonial.objects.all().delete()
        reviews = [
            (
                "Sarah Mitchell",
                "Ajoyib mehmonxona! Xonalar toza, xodimlar juda mehribon.",
                "Прекрасный отель! Номера чистые, персонал очень внимательный.",
                "Wonderful hotel! Clean rooms and very kind staff.",
            ),
            (
                "Aziz Karimov",
                "Buxoroda eng yaxshi tanlov. Nonushta a'lo darajada.",
                "Лучший выбор в Бухаре. Завтрак на высшем уровне.",
                "The best choice in Bukhara. Excellent breakfast.",
            ),
            (
                "Elena Petrova",
                "Lyabi-Hauz yonida ajoyib joy. Albatta yana kelamiz!",
                "Прекрасное место рядом с Ляби-Хауз. Обязательно вернёмся!",
                "Great location near Lyabi-Hauz. We will definitely return!",
            ),
            (
                "James Wilson",
                "Mukammal joylashuv, nafis xonalar va a'lo xizmat.",
                "Идеальное расположение, элегантные номера и отличный сервис.",
                "Perfect location, elegant rooms, and exceptional service.",
            ),
            (
                "Dilnoza Rahimova",
                "Oilaviy dam olish uchun ideal. Bolalar juda xursand bo'ldi.",
                "Идеально для семейного отдыха. Дети были в восторге.",
                "Ideal for a family stay. The children were delighted.",
            ),
        ]
        for i, (name, uz, ru, en) in enumerate(reviews, 1):
            t = Testimonial(guest_name=name, rating=5, ordering=i, is_active=True)
            set_i18n(t, "content", uz, ru, en)
            t.save()
        self.stdout.write("  Testimonials (5)")

    def _faqs(self):
        FAQ.objects.all().delete()
        faqs = [
            (
                "Check-in vaqti qachon?",
                "Check-in soat 14:00 dan boshlanadi. Erta kelish mumkin — joy bo'lsa, xona tayyorlanadi.",
                "Во сколько заезд?",
                "Заезд с 14:00. Ранний заезд возможен при наличии свободных номеров.",
                "What time is check-in?",
                "Check-in starts at 14:00. Early check-in is available subject to availability.",
            ),
            (
                "Check-out vaqti qachon?",
                "Check-out soat 12:00 gacha. Kechikish uchun resepsiyaga murojaat qiling.",
                "Во сколько выезд?",
                "Выезд до 12:00. Для позднего выезда обратитесь на стойку регистрации.",
                "What time is check-out?",
                "Check-out is by 12:00. For late check-out, please contact reception.",
            ),
            (
                "Nonushta kiritilganmi?",
                "Ha, barcha xona turlariga nonushta kiritilgan.",
                "Завтрак включён?",
                "Да, завтрак включён во все типы номеров.",
                "Is breakfast included?",
                "Yes, breakfast is included with all room types.",
            ),
            (
                "Bekor qilish qoidalari qanday?",
                "Kelish sanasidan 48 soat oldin bepul bekor qilish mumkin.",
                "Какие правила отмены?",
                "Бесплатная отмена за 48 часов до даты заезда.",
                "What is the cancellation policy?",
                "Free cancellation up to 48 hours before arrival.",
            ),
            (
                "Aeroport transferi bormi?",
                "Ha, qo'shimcha to'lov evaziga aeroport va vokzal transferi mavjud.",
                "Есть трансфер из аэропорта?",
                "Да, трансфер из аэропорта и вокзала доступен за дополнительную плату.",
                "Is airport transfer available?",
                "Yes, airport and railway transfers are available for an additional fee.",
            ),
            (
                "Bolalar uchun qulayliklar bormi?",
                "Ha, bolalar karavoti va maxsus ovqatlanish so'rov bo'yicha taqdim etiladi.",
                "Есть удобства для детей?",
                "Да, детская кроватка и специальное питание по запросу.",
                "Are there amenities for children?",
                "Yes, cribs and special meals are available on request.",
            ),
        ]
        for i, (uz_q, uz_a, ru_q, ru_a, en_q, en_a) in enumerate(faqs, 1):
            f = FAQ(ordering=i, is_active=True)
            set_i18n(f, "question", uz_q, ru_q, en_q)
            set_i18n(f, "answer", uz_a, ru_a, en_a)
            f.save()
        self.stdout.write("  FAQs (6)")

    def _promotion(self):
        Promotion.objects.all().delete()
        p = Promotion(
            discount_label="-20%",
            is_active=True,
            starts_at=date.today() - timedelta(days=14),
            ends_at=date.today() + timedelta(days=90),
        )
        set_i18n(
            p,
            "title",
            "Yozgi maxsus taklif",
            "Летнее спецпредложение",
            "Summer Special Offer",
        )
        set_i18n(
            p,
            "description",
            "Oldindan bron qiling va 20% chegirma oling",
            "Забронируйте заранее и получите скидку 20%",
            "Book early and save 20%",
        )
        set_i18n(p, "discount_label", "-20%", "-20%", "-20%")
        p.save()
        self.stdout.write("  Promotion")

    def _nearby(self):
        NearbyPlace.objects.all().delete()
        places = [
            ("Lyabi-Hauz maydoni", "5 daqiqa piyoda", "Ансамбль Ляби-Хауз", "5 мин пешком", "Lyabi-Hauz", "5 min walk", "landmark"),
            ("Ark qal'asi", "10 daqiqa piyoda", "Крепость Арк", "10 мин пешком", "Ark Fortress", "10 min walk", "mosque"),
            ("Po-i-Kalyan minora", "12 daqiqa piyoda", "Минaret Калян", "12 мин пешком", "Kalyan Minaret", "12 min walk", "landmark"),
            ("Buxoro aeroporti", "20 daqiqa mashina", "Аэропорт Бухары", "20 мин на машине", "Bukhara Airport", "20 min drive", "plane"),
            ("Buxoro temir yo'l vokzali", "15 daqiqa mashina", "Ж/д вокзал Бухары", "15 мин на машине", "Bukhara Railway Station", "15 min drive", "train"),
        ]
        for i, (uz_n, uz_d, ru_n, ru_d, en_n, en_d, icon) in enumerate(places, 1):
            n = NearbyPlace(icon=icon, ordering=i, is_active=True)
            set_i18n(n, "name", uz_n, ru_n, en_n)
            set_i18n(n, "distance", uz_d, ru_d, en_d)
            n.save()
        self.stdout.write("  Nearby places (5)")

    def _policies(self):
        PolicyPage.objects.all().delete()
        policies = [
            (
                "Maxfiylik siyosati",
                "privacy",
                "Shaxsiy ma'lumotlaringiz himoya qilinadi va uchinchi shaxslarga berilmaydi.",
                "Политика конфиденциальности",
                "Ваши персональные данные защищены и не передаются третьим лицам.",
                "Privacy Policy",
                "Your personal data is protected and not shared with third parties.",
            ),
            (
                "Bekor qilish qoidalari",
                "cancellation",
                "48 soat oldin bepul bekor qilish. Keyinroq — birinchi kecha narxi ushlab qolinadi.",
                "Правила отмены",
                "Бесплатная отмена за 48 часов. Позже удерживается стоимость первой ночи.",
                "Cancellation Policy",
                "Free cancellation 48 hours in advance. Later, the first night is charged.",
            ),
            (
                "Mehmonxona qoidalari",
                "house-rules",
                "Iltimos, boshqa mehmonlarni bezovta qilmang. Sigaret chekish faqat belgilangan joylarda.",
                "Правила отеля",
                "Пожалуйста, не беспокойте других гостей. Курение только в отведённых местах.",
                "House Rules",
                "Please do not disturb other guests. Smoking is allowed only in designated areas.",
            ),
        ]
        for uz_t, slug, uz_c, ru_t, ru_c, en_t, en_c in policies:
            p = PolicyPage(slug=slug, is_active=True)
            set_i18n(p, "title", uz_t, ru_t, en_t)
            set_i18n(p, "content", uz_c, ru_c, en_c)
            p.save()
        self.stdout.write("  Policy pages (3)")

    def _rooms(self):
        RoomType.objects.all().delete()
        types_data = [
            (
                "2 alohida karavotli deluxe ikki kishilik xona",
                "deluxe-twin",
                "Ikki alohida karavot, qulay ish zonasi va nafis interyerga ega deluxe xona.",
                "Двухместный номер Делюкс с 2 отдельными кроватями",
                "Просторный номер делюкс с двумя отдельными кроватями, рабочей зоной и элегантным интерьером.",
                "Deluxe Double Room with 2 Separate Beds",
                "A spacious deluxe room with two separate beds, a work area, and elegant interiors.",
                Decimal("650000"),
                2,
                28,
                (42, 34, 26),
            ),
            (
                "1 katta karavotli deluxe ikki kishilik xona",
                "deluxe-king",
                "Katta karavot, eski shahar ruhidagi bezak va premium qulayliklarga ega deluxe xona.",
                "Двухместный номер Делюкс с 1 большой кроватью",
                "Номер делюкс с одной большой кроватью, интерьером в духе старой Бухары и премиальными удобствами.",
                "Deluxe Double Room with 1 Large Bed",
                "A deluxe room with one large bed, old-city inspired decor, and premium amenities.",
                Decimal("720000"),
                2,
                30,
                (61, 46, 32),
            ),
            (
                "1 yotoq xonali lyuks",
                "one-bedroom-suite",
                "Alohida yotoqxona va dam olish zonasi bo'lgan keng lyuks.",
                "Люкс с 1 спальней",
                "Просторный люкс с отдельной спальней и уютной гостевой зоной.",
                "One-Bedroom Suite",
                "A spacious suite with a separate bedroom and a cozy lounge area.",
                Decimal("1100000"),
                3,
                45,
                (20, 18, 16),
            ),
            (
                "Hashamatli uch kishilik xona",
                "luxury-triple",
                "Uch mehmon uchun mo'ljallangan, keng va hashamatli oilaviy xona.",
                "Роскошный трехместный номер",
                "Просторный роскошный номер для троих гостей, идеально подходящий для семьи или друзей.",
                "Luxury Triple Room",
                "A spacious luxury room for three guests, ideal for families or friends.",
                Decimal("900000"),
                3,
                36,
                (84, 58, 36),
            ),
        ]
        room_types = []
        for i, (uz_n, slug, uz_d, ru_n, ru_d, en_n, en_d, price, cap, sqm, color) in enumerate(types_data, 1):
            rt = RoomType(
                slug=slug,
                base_price=price,
                capacity=cap,
                size_sqm=sqm,
                ordering=i,
                is_active=True,
            )
            set_i18n(rt, "name", uz_n, ru_n, en_n)
            set_i18n(rt, "description", uz_d, ru_d, en_d)
            rt.save()
            for j in range(1, 4):
                ri = RoomImage(room_type=rt, caption=f"{uz_n} — {j}", ordering=j, is_primary=(j == 1))
                ri.image.save(f"room_{slug}_{j}.jpg", make_placeholder(f"room_{slug}_{j}.jpg", bg=color, label=uz_n), save=True)
            room_types.append(rt)

        rooms_map = {
            "deluxe-twin": [(f"10{i}", 1) for i in range(1, 7)],
            "deluxe-king": [(f"20{i}", 2) for i in range(1, 7)],
            "one-bedroom-suite": [(f"30{i}", 3) for i in range(1, 5)],
            "luxury-triple": [(f"40{i}", 4) for i in range(1, 5)],
        }
        for rt in room_types:
            for num, floor in rooms_map[rt.slug]:
                Room.objects.create(room_type=rt, number=num, floor=floor, is_active=True)

        BlockedDate.objects.all().delete()
        suite_room = Room.objects.get(number="301")
        BlockedDate.objects.create(
            room=suite_room,
            start_date=date.today() + timedelta(days=10),
            end_date=date.today() + timedelta(days=12),
            reason="Ta'mirlash",
        )
        self.stdout.write("  Room types (4), rooms (20), images, blocked date")
        return room_types

    def _seasonal_prices(self, room_types):
        SeasonalPrice.objects.all().delete()
        summer_start = date(date.today().year, 6, 1)
        summer_end = date(date.today().year, 8, 31)
        for rt in room_types:
            SeasonalPrice.objects.create(
                room_type=rt,
                start_date=summer_start,
                end_date=summer_end,
                price=rt.base_price * Decimal("1.25"),
            )
        self.stdout.write("  Seasonal prices")

    def _sample_bookings(self, room_types):
        Booking.objects.all().delete()
        standard = room_types[0]
        rooms = list(Room.objects.filter(room_type=standard)[:2])

        create_booking(
            guest_name="Javohir Toshmatov",
            email="javohir@example.com",
            phone="+998901234567",
            guests_count=2,
            check_in=date.today() + timedelta(days=3),
            check_out=date.today() + timedelta(days=6),
            room_type=standard,
            room_ids=[rooms[0].pk],
            special_requests="Kechki check-in, taxminan 22:00",
        )
        b2 = create_booking(
            guest_name="Maria Schmidt",
            email="maria@example.com",
            phone="+491701234567",
            guests_count=2,
            check_in=date.today() + timedelta(days=7),
            check_out=date.today() + timedelta(days=10),
            room_type=standard,
            room_ids=[rooms[1].pk],
            special_requests="",
        )
        b2.status = Booking.Status.CONFIRMED
        b2.save()
        self.stdout.write("  Sample bookings (2)")
