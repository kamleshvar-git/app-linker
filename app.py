from flask import Flask, render_template_string, request, redirect, url_for, session, flash
import sqlite3
import hashlib
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = os.urandom(24)

DATABASE = 'app_linker.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS websites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            link TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS remarks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            website_name TEXT,
            website_url TEXT,
            visit_time DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    default_websites = [
        # General Shopping
        ('Amazon India', 'General Shopping', 'https://amazon.in'),
        ('Flipkart', 'General Shopping', 'https://flipkart.com'),
        ('Meesho', 'General Shopping', 'https://meesho.com'),
        ('Snapdeal', 'General Shopping', 'https://snapdeal.com'),
        ('Paytm Mall', 'General Shopping', 'https://paytmmall.com'),
        ('Tata CLiQ', 'General Shopping', 'https://tatacliq.com'),
        ('ShopClues', 'General Shopping', 'https://shopclues.com'),
        ('IndiaMART', 'General Shopping', 'https://indiamart.com'),
        ('TradeIndia', 'General Shopping', 'https://tradeindia.com'),
        ('GlowRoad', 'General Shopping', 'https://glowroad.com'),
        ('ClickOnCare', 'General Shopping', 'https://clickoncare.com'),
        ('Junglee', 'General Shopping', 'https://junglee.com'),
        ('Yaari', 'General Shopping', 'https://yaari.com'),
        ('Mall91', 'General Shopping', 'https://mall91.com'),
        # Fashion & Clothing
        ('Myntra', 'Fashion & Clothing', 'https://myntra.com'),
        ('Ajio', 'Fashion & Clothing', 'https://ajio.com'),
        ('Limeroad', 'Fashion & Clothing', 'https://limeroad.com'),
        ('Voonik', 'Fashion & Clothing', 'https://voonik.com'),
        ('Urbanic', 'Fashion & Clothing', 'https://urbanic.com'),
        ('Savana', 'Fashion & Clothing', 'https://savana.com'),
        ('Koovs', 'Fashion & Clothing', 'https://koovs.com'),
        ('StalkBuyLove', 'Fashion & Clothing', 'https://stalkbuylove.com'),
        ('Zivame', 'Fashion & Clothing', 'https://zivame.com'),
        ('Clovia', 'Fashion & Clothing', 'https://clovia.com'),
        ('Biba', 'Fashion & Clothing', 'https://biba.in'),
        ('FabIndia', 'Fashion & Clothing', 'https://fabindia.com'),
        ('Global Desi', 'Fashion & Clothing', 'https://globaldesi.in'),
        ('AND', 'Fashion & Clothing', 'https://andindia.com'),
        ('W for Woman', 'Fashion & Clothing', 'https://wforwoman.com'),
        ('Cover Story', 'Fashion & Clothing', 'https://coverstory.co.in'),
        ('The Souled Store', 'Fashion & Clothing', 'https://thesouledstore.com'),
        ('Bewakoof', 'Fashion & Clothing', 'https://bewakoof.com'),
        ('Rare Rabbit', 'Fashion & Clothing', 'https://rarerabbit.in'),
        ('Snitch', 'Fashion & Clothing', 'https://snitch.co.in'),
        ('Off Duty', 'Fashion & Clothing', 'https://offduty.in'),
        # Beauty & Personal Care
        ('Nykaa', 'Beauty & Personal Care', 'https://nykaa.com'),
        ('Purplle', 'Beauty & Personal Care', 'https://purplle.com'),
        ('MyGlamm', 'Beauty & Personal Care', 'https://myglamm.com'),
        ('Mamaearth', 'Beauty & Personal Care', 'https://mamaearth.in'),
        ('Wow Skin Science', 'Beauty & Personal Care', 'https://wowskin.in'),
        ('Sugar Cosmetics', 'Beauty & Personal Care', 'https://trysugar.com'),
        ('Plum Goodness', 'Beauty & Personal Care', 'https://plumgoodness.com'),
        ('mcaffeine', 'Beauty & Personal Care', 'https://mcaffeine.com'),
        ('Lotus Herbals', 'Beauty & Personal Care', 'https://lotusherbals.com'),
        ('Forest Essentials', 'Beauty & Personal Care', 'https://forestessentialsindia.com'),
        ('The Moms Co', 'Beauty & Personal Care', 'https://themomsco.com'),
        ('Khadi Natural', 'Beauty & Personal Care', 'https://khadinatural.com'),
        # Electronics
        ('Croma', 'Electronics', 'https://croma.com'),
        ('Reliance Digital', 'Electronics', 'https://reliancedigital.in'),
        ('Vijay Sales', 'Electronics', 'https://vijaysales.com'),
        ('Poorvika Mobiles', 'Electronics', 'https://poorvika.com'),
        ('Sangeetha Mobiles', 'Electronics', 'https://sangeethamobiles.com'),
        ('MDComputers', 'Electronics', 'https://mdcomputers.in'),
        ('PrimeABGB', 'Electronics', 'https://primeabgb.com'),
        ('Vedant Computers', 'Electronics', 'https://vedantcomputers.com'),
        ('ElectroWorld', 'Electronics', 'https://electroworld.in'),
        ('ITDepot', 'Electronics', 'https://theitdepot.com'),
        # Furniture & Home
        ('Pepperfry', 'Furniture & Home', 'https://pepperfry.com'),
        ('Urban Ladder', 'Furniture & Home', 'https://urbanladder.com'),
        ('HomeTown', 'Furniture & Home', 'https://hometown.in'),
        ('WoodenStreet', 'Furniture & Home', 'https://woodenstreet.com'),
        ('Nilkamal Furniture', 'Furniture & Home', 'https://nilkamalfurniture.com'),
        ('Rentomojo', 'Furniture & Home', 'https://rentomojo.com'),
        ('Furlenco', 'Furniture & Home', 'https://furlenco.com'),
        ('Home Centre', 'Furniture & Home', 'https://homecentre.in'),
        ('Address Home', 'Furniture & Home', 'https://addresshome.com'),
        ('Durian Furniture', 'Furniture & Home', 'https://durian.in'),
        ('Saraf Furniture', 'Furniture & Home', 'https://insaraf.com'),
        ('Wooden Twist', 'Furniture & Home', 'https://woodentwist.com'),
        # Grocery & Daily Needs
        ('BigBasket', 'Grocery & Daily Needs', 'https://bigbasket.com'),
        ('Blinkit', 'Grocery & Daily Needs', 'https://blinkit.com'),
        ('Zepto', 'Grocery & Daily Needs', 'https://zepto.com'),
        ('JioMart', 'Grocery & Daily Needs', 'https://jiomart.com'),
        ("Nature's Basket", 'Grocery & Daily Needs', 'https://naturesbasket.co.in'),
        ("Spencer's", 'Grocery & Daily Needs', 'https://spencers.in'),
        ('Easyday', 'Grocery & Daily Needs', 'https://easyday.in'),
        ('Milkbasket', 'Grocery & Daily Needs', 'https://milkbasket.com'),
        ('BB Daily', 'Grocery & Daily Needs', 'https://bbdaily.com'),
        ('Supr Daily', 'Grocery & Daily Needs', 'https://suprdaily.com'),
        ('Dunzo', 'Grocery & Daily Needs', 'https://dunzo.com'),
        ('Swiggy Instamart', 'Grocery & Daily Needs', 'https://swiggy.com/instamart'),
        ('Amazon Pantry', 'Grocery & Daily Needs', 'https://amazon.in/pantry'),
        ('Flipkart Grocery', 'Grocery & Daily Needs', 'https://flipkart.com/grocery'),
        # Baby & Kids
        ('FirstCry', 'Baby & Kids', 'https://firstcry.com'),
        ('Hopscotch', 'Baby & Kids', 'https://hopscotch.in'),
        ('Babyhug', 'Baby & Kids', 'https://babyhug.in'),
        ('Kidstoppress', 'Baby & Kids', 'https://kidstoppress.com'),
        ('Shumee', 'Baby & Kids', 'https://shumee.in'),
        ('TinyStep', 'Baby & Kids', 'https://tinystep.in'),
        ('MiniKlub', 'Baby & Kids', 'https://miniklub.in'),
        # Jewellery & Luxury
        ('CaratLane', 'Jewellery & Luxury', 'https://caratlane.com'),
        ('Bluestone', 'Jewellery & Luxury', 'https://bluestone.com'),
        ('Luxepolis', 'Jewellery & Luxury', 'https://luxepolis.com'),
        ('Tanishq', 'Jewellery & Luxury', 'https://tanishq.co.in'),
        ('Kalyan Jewellers', 'Jewellery & Luxury', 'https://kalyanjewellers.net'),
        ('Malabar Gold', 'Jewellery & Luxury', 'https://malabargoldanddiamonds.com'),
        ('Voylla', 'Jewellery & Luxury', 'https://voylla.com'),
        ('PC Jeweller', 'Jewellery & Luxury', 'https://pcjeweller.com'),
        # Handicrafts & Ethnic
        ('Craftsvilla', 'Handicrafts & Ethnic', 'https://craftsvilla.com'),
        ('Jaypore', 'Handicrafts & Ethnic', 'https://jaypore.com'),
        ('Okhai', 'Handicrafts & Ethnic', 'https://okhai.org'),
        ('iTokri', 'Handicrafts & Ethnic', 'https://itokri.com'),
        ('Gaatha', 'Handicrafts & Ethnic', 'https://gaatha.com'),
        ('Peepul Tree', 'Handicrafts & Ethnic', 'https://peepultree.world'),
        ('India Craft House', 'Handicrafts & Ethnic', 'https://indiacrafthouse.com'),
        # Books & Education
        ('Amazon Kindle', 'Books & Education', 'https://amazon.in/kindle-dbs/storefront'),
        ('Flipkart Books', 'Books & Education', 'https://flipkart.com/books-store'),
        ('Sapna Book House', 'Books & Education', 'https://sapnaonline.com'),
        ('Crossword', 'Books & Education', 'https://crossword.in'),
        ('Bookswagon', 'Books & Education', 'https://bookswagon.com'),
        ('Exotic India Art', 'Books & Education', 'https://exoticindiaart.com'),
        ('PustakMandi', 'Books & Education', 'https://pustakmandi.com'),
        # International
        ('AliExpress', 'International', 'https://aliexpress.com'),
        ('Etsy', 'International', 'https://etsy.com'),
        ('Ubuy India', 'International', 'https://ubuy.co.in'),
        ('Banggood', 'International', 'https://banggood.com'),
        ('Gearbest', 'International', 'https://gearbest.com'),
        ('DHgate', 'International', 'https://dhgate.com'),
        ('Wish', 'International', 'https://wish.com'),
        ('Overstock', 'International', 'https://overstock.com'),
        ('Newegg', 'International', 'https://newegg.com'),
        ('Rakuten', 'International', 'https://rakuten.com'),
        ('Walmart', 'International', 'https://walmart.com'),
        ('Target', 'International', 'https://target.com'),
        ('BestBuy', 'International', 'https://bestbuy.com'),
        # Fitness & Sports
        ('Decathlon', 'Fitness & Sports', 'https://decathlon.in'),
        ('HealthKart', 'Fitness & Sports', 'https://healthkart.com'),
        ('Cultsport', 'Fitness & Sports', 'https://cultsport.com'),
        ('Fitshop', 'Fitness & Sports', 'https://fitshop.co.in'),
        ('Boldfit', 'Fitness & Sports', 'https://boldfit.in'),
        # Fashion & Clothing (Additional)
        ('Tata CLiQ Fashion', 'Fashion & Clothing', 'https://tatacliqfashion.com'),
        ('Nykaa Fashion', 'Fashion & Clothing', 'https://nykaafashion.com'),
        ('Zara', 'Fashion & Clothing', 'https://zara.com'),
        ('H&M', 'Fashion & Clothing', 'https://hm.com'),
        ('Forever 21', 'Fashion & Clothing', 'https://forever21.in'),
        ('Pantaloons', 'Fashion & Clothing', 'https://pantaloons.com'),
        ('Shoppers Stop', 'Fashion & Clothing', 'https://shoppersstop.com'),
        # Footwear
        ('Bata', 'Footwear', 'https://bata.in'),
        ('Red Tape', 'Footwear', 'https://redtape.com'),
        ('Woodland', 'Footwear', 'https://woodlandworldwide.com'),
        ('Metro Shoes', 'Footwear', 'https://metroshoes.com'),
        ('Khadims', 'Footwear', 'https://khadims.com'),
        # Beauty & Personal Care (Additional)
        ('Wow Products', 'Beauty & Personal Care', 'https://wowproducts.com'),
        ('Biotique', 'Beauty & Personal Care', 'https://biotique.com'),
        # Electronics (Additional)
        ('Mi India', 'Electronics', 'https://mi.com'),
        ('Samsung India', 'Electronics', 'https://samsung.com/in'),
        ('OnePlus', 'Electronics', 'https://oneplus.in'),
        ('Realme', 'Electronics', 'https://realme.com'),
        ('boAt', 'Electronics', 'https://boat-lifestyle.com'),
        ('Clarion Computers', 'Electronics', 'https://clarioncomputers.in'),
        # Furniture & Home (Additional)
        ('Fabindia Home', 'Furniture & Home', 'https://fabindia.com'),
        # Food Delivery & Restaurants
        ('Swiggy', 'Food Delivery', 'https://swiggy.com'),
        ('Zomato', 'Food Delivery', 'https://zomato.com'),
        ("Domino's India", 'Food Delivery', 'https://dominos.co.in'),
        ('Pizza Hut India', 'Food Delivery', 'https://pizzahut.co.in'),
        ('KFC India', 'Food Delivery', 'https://kfc.co.in'),
        # Books & Education (Additional)
        ('Bookchor', 'Books & Education', 'https://bookchor.com'),
        ('Kitabay', 'Books & Education', 'https://kitabay.com'),
        ('Scholastic India', 'Books & Education', 'https://scholastic.co.in'),
        # Gaming
        ('Games The Shop', 'Gaming', 'https://gamestheshop.com'),
        ('mCube Games', 'Gaming', 'https://mcubegames.in'),
        ('Prepaid Gamer Card', 'Gaming', 'https://prepaidgamercard.com'),
        ('Xbox', 'Gaming', 'https://xbox.com'),
        ('PlayStation', 'Gaming', 'https://playstation.com'),
        # Baby & Kids (Additional)
        ('Hamleys', 'Baby & Kids', 'https://hamleys.in'),
        ('Toycra', 'Baby & Kids', 'https://toycra.com'),
        ('Kids Stoppress', 'Baby & Kids', 'https://kidsstoppress.com'),
        # Health & Pharmacy
        ('Netmeds', 'Health & Pharmacy', 'https://netmeds.com'),
        ('PharmEasy', 'Health & Pharmacy', 'https://pharmeasy.in'),
        ('1mg', 'Health & Pharmacy', 'https://1mg.com'),
        ('Apollo Pharmacy', 'Health & Pharmacy', 'https://apollopharmacy.in'),
        ('Medlife', 'Health & Pharmacy', 'https://medlife.com'),
        # Fitness & Sports (Additional)
        ('Nutrabay', 'Fitness & Sports', 'https://nutrabay.com'),
        ('MuscleBlaze', 'Fitness & Sports', 'https://muscleblaze.com'),
        # International (Additional)
        ('Shein', 'International', 'https://shein.com'),
        # Coupons & Deals
        ('GrabOn', 'Coupons & Deals', 'https://grabon.in'),
        ('CouponRaja', 'Coupons & Deals', 'https://couponraja.in'),
        ('CashKaro', 'Coupons & Deals', 'https://cashkaro.com'),
        ('Nearbuy', 'Coupons & Deals', 'https://nearbuy.com'),
        ('FreeKaaMaal', 'Coupons & Deals', 'https://freekaamaal.com'),
        ('Boodmo', 'Coupons & Deals', 'https://boodmo.com'),
        # Automotive
        ('99rpm', 'Automotive', 'https://99rpm.com'),
        ('CarHatke', 'Automotive', 'https://carhatke.com'),
        ('TyreDekho', 'Automotive', 'https://tyredekho.com'),
        ('Gaadi', 'Automotive', 'https://gaadi.com'),
        # Pets
        ('Heads Up For Tails', 'Pets', 'https://headsupfortails.com'),
        ('PetsWorld', 'Pets', 'https://petsworld.in'),
        ('Pet Warehouse', 'Pets', 'https://petwarehouse.in'),
        ('DogSpot', 'Pets', 'https://dogspot.in'),
        ('Zigly', 'Pets', 'https://zigly.com'),
        # Gifts & Flowers
        ('Ferns N Petals', 'Gifts & Flowers', 'https://fnp.com'),
        ('IGP', 'Gifts & Flowers', 'https://igp.com'),
        ('Archies', 'Gifts & Flowers', 'https://archiesonline.com'),
        ('My Flower Tree', 'Gifts & Flowers', 'https://myflowertree.com'),
        ('FlowerAura', 'Gifts & Flowers', 'https://floweraura.com'),
        # Travel
        ('MakeMyTrip', 'Travel', 'https://makemytrip.com'),
        ('Yatra', 'Travel', 'https://yatra.com'),
        ('Cleartrip', 'Travel', 'https://cleartrip.com'),
        ('Goibibo', 'Travel', 'https://goibibo.com'),
        ('Booking.com', 'Travel', 'https://booking.com'),
        # Payments & Wallets
        ('Paytm', 'Payments & Wallets', 'https://paytm.com'),
        ('PhonePe', 'Payments & Wallets', 'https://phonepe.com'),
        ('Google Pay', 'Payments & Wallets', 'https://googlepay.com'),
        ('Amazon Pay', 'Payments & Wallets', 'https://amazonpay.in'),
        ('MobiKwik', 'Payments & Wallets', 'https://mobikwik.com'),
        # Handicrafts & Ethnic (Additional)
        ('Udaan', 'Handicrafts & Ethnic', 'https://udaan.com'),
        ('ExportersIndia', 'Handicrafts & Ethnic', 'https://exportersindia.com'),
        ('Alibaba', 'Handicrafts & Ethnic', 'https://alibaba.com'),
        # Logistics & Shipping
        ('Delhivery', 'Logistics & Shipping', 'https://delhivery.com'),
        ('BlueDart', 'Logistics & Shipping', 'https://bluedart.com'),
        ('DTDC', 'Logistics & Shipping', 'https://dtdc.in'),
        ('India Post', 'Logistics & Shipping', 'https://indiapost.gov.in'),
        ('ShipRocket', 'Logistics & Shipping', 'https://shiprocket.in'),
        # Organic & Natural
        ('Organic India', 'Organic & Natural', 'https://organicindia.com'),
        ('The Organic World', 'Organic & Natural', 'https://theorganicworld.com'),
        ('Conscious Food', 'Organic & Natural', 'https://consciousfood.com'),
        ('Phalada Agro', 'Organic & Natural', 'https://phaladaagro.com'),
        ('24 Mantra', 'Organic & Natural', 'https://24mantra.com'),
        ('The Box Walla', 'Organic & Natural', 'https://theboxwalla.com'),
        ('Snackible', 'Organic & Natural', 'https://snackible.com'),
        # Men's Grooming
        ('Bombay Shaving Company', "Men's Grooming", 'https://bombayshavingcompany.com'),
        ('The Man Company', "Men's Grooming", 'https://themancompany.com'),
        ('Ustraa', "Men's Grooming", 'https://ustraa.com'),
        # Freelance & Digital Services
        ('Fiverr', 'Freelance & Digital', 'https://fiverr.com'),
        ('Upwork', 'Freelance & Digital', 'https://upwork.com'),
        ('Freelancer', 'Freelance & Digital', 'https://freelancer.com'),
        ('Envato', 'Freelance & Digital', 'https://envato.com'),
        ('Gumroad', 'Freelance & Digital', 'https://gumroad.com'),
        # Cameras & Photography
        ('Nikon India', 'Cameras & Photography', 'https://nikon.co.in'),
        ('Canon India', 'Cameras & Photography', 'https://canon.co.in'),
        ('Sony India', 'Cameras & Photography', 'https://sony.co.in'),
        ('GoPro', 'Cameras & Photography', 'https://gopro.com'),
        # Audio & Headphones
        ('Digiitek', 'Audio & Headphones', 'https://digiitek.com'),
        ('JBL', 'Audio & Headphones', 'https://jbl.com'),
        ('Sennheiser', 'Audio & Headphones', 'https://sennheiser.com'),
        ('Bose India', 'Audio & Headphones', 'https://boseindia.com'),
        ('Skullcandy', 'Audio & Headphones', 'https://skullcandy.in'),
        ('Zebronics', 'Audio & Headphones', 'https://zebronics.com'),
        # Home Services
        ('uClean', 'Home Services', 'https://uclean.in'),
        ('Urban Company', 'Home Services', 'https://urbancompany.com'),
        ('HouseJoy', 'Home Services', 'https://housejoy.in'),
        ('Clean Fanatics', 'Home Services', 'https://cleanfanatics.in'),
        ('Helpr', 'Home Services', 'https://helpr.in'),
        # Online Learning
        ('Coursera', 'Online Learning', 'https://coursera.org'),
        ('Udemy', 'Online Learning', 'https://udemy.com'),
        ('edX', 'Online Learning', 'https://edx.org'),
        ('Skillshare', 'Online Learning', 'https://skillshare.com'),
        ('Unacademy', 'Online Learning', 'https://unacademy.com'),
        # Electronics Components & DIY
        ('Raspberry Pi', 'Electronics Components', 'https://raspberrypi.com'),
        ('Arduino', 'Electronics Components', 'https://arduino.cc'),
        ('Robu', 'Electronics Components', 'https://robu.in'),
        ('Electronics Comp', 'Electronics Components', 'https://electronicscomp.com'),
        ('ThingBits', 'Electronics Components', 'https://thingbits.in'),
        # App Stores
        ('Google Play Store', 'App Stores', 'https://play.google.com'),
        ('Apple App Store', 'App Stores', 'https://apps.apple.com'),
        ('APKPure', 'App Stores', 'https://apkpure.com'),
        ('APKMirror', 'App Stores', 'https://apkmirror.com'),
        ('Uptodown', 'App Stores', 'https://uptodown.com'),
        # Office & Stationery
        ('Office Stock', 'Office & Stationery', 'https://officestock.in'),
        ('Scooboo', 'Office & Stationery', 'https://scooboo.in'),
        ('Printvenue', 'Office & Stationery', 'https://printvenue.com'),
        ('VistaPrint India', 'Office & Stationery', 'https://vistaprint.in'),
        ('Staples India', 'Office & Stationery', 'https://staples.in'),
        # Real Estate
        ('99acres', 'Real Estate', 'https://99acres.com'),
        ('MagicBricks', 'Real Estate', 'https://magicbricks.com'),
        ('Housing.com', 'Real Estate', 'https://housing.com'),
        ('NoBroker', 'Real Estate', 'https://nobroker.in'),
        ('Square Yards', 'Real Estate', 'https://squareyards.com'),
        # Streaming & Entertainment
        ('Netflix', 'Streaming & Entertainment', 'https://netflix.com'),
        ('Prime Video', 'Streaming & Entertainment', 'https://primevideo.com'),
        ('Disney+ Hotstar', 'Streaming & Entertainment', 'https://hotstar.com'),
        ('SonyLIV', 'Streaming & Entertainment', 'https://sonyliv.com'),
        ('ZEE5', 'Streaming & Entertainment', 'https://zee5.com'),
        # Home Appliances
        ('Prestige Home Appliances', 'Home Appliances', 'https://prestigehomeappliances.com'),
        ('Pigeon India', 'Home Appliances', 'https://pigeonindia.com'),
        ('Wonderchef', 'Home Appliances', 'https://wonderchef.com'),
        ('Borosil', 'Home Appliances', 'https://borosil.com'),
        ('Elgi Ultra', 'Home Appliances', 'https://elgiultra.com'),
        # Classifieds
        ('Quickr', 'Classifieds', 'https://quickr.com'),
        ('OLX India', 'Classifieds', 'https://olx.in'),
        ('ClickIndia', 'Classifieds', 'https://clickindia.com'),
        ('Sulekha', 'Classifieds', 'https://sulekha.com'),
        # General Shopping (Additional)
        ('India Bazaar Online', 'General Shopping', 'https://indiabazaaronline.com'),
        ('Flipkart Wholesale', 'General Shopping', 'https://flipkartwholesale.com'),
        ('Grofers', 'General Shopping', 'https://grofers.com'),
    ]

    cursor.execute('SELECT COUNT(*) FROM websites')
    if cursor.fetchone()[0] == 0:
        cursor.executemany('INSERT INTO websites (name, category, link) VALUES (?, ?, ?)', default_websites)
    else:
        for name, category, link in default_websites:
            cursor.execute('SELECT COUNT(*) FROM websites WHERE name = ? OR link = ?', (name, link))
            if cursor.fetchone()[0] == 0:
                cursor.execute('INSERT INTO websites (name, category, link) VALUES (?, ?, ?)', (name, category, link))

    conn.commit()
    conn.close()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        if not session.get('is_admin'):
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# ============================================================================
# PREMIUM BASE TEMPLATE - AMAZON/FLIPKART STYLE
# ============================================================================
BASE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} - App Linker</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        /* ==================== CSS VARIABLES FOR THEMING ==================== */
        :root {
            --primary-color: #2874f0;
            --primary-hover: #1e5fc7;
            --secondary-color: #fb641b;
            --secondary-hover: #e55a10;
            --accent-color: #ffd700;
            --success-color: #10b981;
            --error-color: #ef4444;
            --warning-color: #f59e0b;
            --info-color: #3b82f6;

            /* Light Mode (Default) */
            --bg-body: #f1f3f6;
            --bg-header: #ffffff;
            --bg-header-top: #172337;
            --bg-card: #ffffff;
            --bg-card-hover: #f8f9fa;
            --bg-section: #ffffff;
            --bg-input: #ffffff;
            --bg-footer: #172337;
            --bg-badge: #e8f4fd;

            --text-primary: #172337;
            --text-secondary: #626262;
            --text-muted: #878787;
            --text-light: #ffffff;
            --text-on-primary: #ffffff;

            --border-color: #e0e0e0;
            --border-light: #f0f0f0;
            --shadow-sm: 0 1px 3px rgba(0,0,0,0.08);
            --shadow-md: 0 4px 12px rgba(0,0,0,0.1);
            --shadow-lg: 0 8px 24px rgba(0,0,0,0.12);
            --shadow-xl: 0 12px 48px rgba(0,0,0,0.16);
            --shadow-glow: 0 0 24px rgba(40, 116, 240, 0.35);

            --gradient-hero: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            --gradient-primary: linear-gradient(135deg, #2874f0 0%, #1a5bb8 100%);
            --gradient-secondary: linear-gradient(135deg, #fb641b 0%, #d84a0a 100%);
            --gradient-gold: linear-gradient(135deg, #ffd700 0%, #ffb300 100%);
            --gradient-success: linear-gradient(135deg, #10b981 0%, #059669 100%);
            --gradient-dark: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);

            --radius-sm: 8px;
            --radius-md: 12px;
            --radius-lg: 16px;
            --radius-xl: 24px;
            --radius-full: 9999px;

            --transition-fast: 0.15s ease;
            --transition-base: 0.3s ease;
            --transition-slow: 0.5s ease;
        }

        [data-theme="dark"] {
            --bg-body: #0f1115;
            --bg-header: #1a1d24;
            --bg-header-top: #0a0b0d;
            --bg-card: #1e2229;
            --bg-card-hover: #252a33;
            --bg-section: #1a1d24;
            --bg-input: #252a33;
            --bg-footer: #0a0b0d;
            --bg-badge: #2d3748;

            --text-primary: #e8e8e8;
            --text-secondary: #a0a0a0;
            --text-muted: #6e6e6e;
            --text-light: #ffffff;
            --text-on-primary: #ffffff;

            --border-color: #2a2f3a;
            --border-light: #1f2329;
            --shadow-sm: 0 1px 3px rgba(0,0,0,0.4);
            --shadow-md: 0 4px 12px rgba(0,0,0,0.5);
            --shadow-lg: 0 8px 24px rgba(0,0,0,0.6);
            --shadow-xl: 0 12px 48px rgba(0,0,0,0.7);
            --shadow-glow: 0 0 24px rgba(40, 116, 240, 0.45);
        }

        /* ==================== RESET & BASE ==================== */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        html {
            scroll-behavior: smooth;
            font-size: 16px;
        }

        body {
            font-family: 'Poppins', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg-body);
            color: var(--text-primary);
            min-height: 100vh;
            transition: background-color var(--transition-base), color var(--transition-base);
            line-height: 1.6;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }

        a {
            text-decoration: none;
            color: inherit;
            transition: color var(--transition-fast);
        }

        button {
            font-family: inherit;
            cursor: pointer;
            border: none;
            outline: none;
            background: none;
        }

        img {
            max-width: 100%;
            height: auto;
        }

        /* ==================== PREMIUM NAVBAR ==================== */
        .sticky-header {
            position: sticky;
            top: 0;
            z-index: 1000;
            background: var(--bg-header);
            box-shadow: var(--shadow-md);
            transition: all var(--transition-base);
        }

        .sticky-header.scrolled {
            box-shadow: var(--shadow-xl);
        }

        /* Top Bar */
        .header-top {
            background: var(--bg-header-top);
            padding: 8px 0;
            font-size: 0.8rem;
        }

        .header-top .container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
        }

        .top-announcement {
            color: var(--text-light);
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .top-announcement i {
            color: var(--accent-color);
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        .top-links {
            display: flex;
            align-items: center;
            gap: 20px;
        }

        .top-links a {
            color: var(--text-light);
            font-weight: 500;
            transition: opacity var(--transition-fast);
            display: flex;
            align-items: center;
            gap: 5px;
        }

        .top-links a:hover {
            opacity: 0.85;
        }

        /* Main Header */
        .header-main {
            padding: 14px 0;
        }

        .header-main .container {
            display: flex;
            align-items: center;
            gap: 24px;
            flex-wrap: wrap;
        }

        /* Logo */
        .logo {
            display: flex;
            align-items: center;
            gap: 12px;
            transition: transform var(--transition-fast);
        }

        .logo:hover {
            transform: scale(1.02);
        }

        .logo-icon {
            width: 50px;
            height: 50px;
            background: var(--gradient-primary);
            border-radius: var(--radius-md);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.6rem;
            box-shadow: var(--shadow-md);
            position: relative;
            overflow: hidden;
        }

        .logo-icon::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: linear-gradient(45deg, transparent, rgba(255,255,255,0.2), transparent);
            transform: rotate(45deg);
            animation: shine 3s infinite;
        }

        @keyframes shine {
            0% { transform: translateX(-100%) rotate(45deg); }
            100% { transform: translateX(100%) rotate(45deg); }
        }

        .logo-text {
            display: flex;
            flex-direction: column;
            line-height: 1.2;
        }

        .logo-text .brand {
            font-size: 1.4rem;
            font-weight: 800;
            background: var(--gradient-primary);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            letter-spacing: -0.5px;
        }

        .logo-text .tagline {
            font-size: 0.7rem;
            color: var(--text-secondary);
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        /* Search Bar */
        .search-container {
            flex: 1;
            min-width: 300px;
            max-width: 650px;
            position: relative;
        }

        .search-box-wrapper {
            position: relative;
            display: flex;
            align-items: center;
        }

        .search-box {
            width: 100%;
            padding: 13px 55px 13px 22px;
            font-size: 0.95rem;
            font-family: inherit;
            background: var(--bg-input);
            border: 2px solid var(--border-color);
            border-radius: var(--radius-full);
            color: var(--text-primary);
            transition: all var(--transition-base);
        }

        .search-box:focus {
            border-color: var(--primary-color);
            box-shadow: var(--shadow-glow);
            background: var(--bg-card);
        }

        .search-box::placeholder {
            color: var(--text-muted);
        }

        .search-btn {
            position: absolute;
            right: 8px;
            width: 40px;
            height: 40px;
            background: var(--gradient-primary);
            border-radius: var(--radius-full);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.1rem;
            color: white;
            transition: all var(--transition-fast);
        }

        .search-btn:hover {
            transform: scale(1.08);
            box-shadow: var(--shadow-md);
        }

        /* Nav Actions */
        .nav-actions {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-left: auto;
        }

        .theme-toggle {
            width: 46px;
            height: 46px;
            background: var(--bg-card);
            border: 2px solid var(--border-color);
            border-radius: var(--radius-md);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.3rem;
            color: var(--text-primary);
            transition: all var(--transition-base);
        }

        .theme-toggle:hover {
            border-color: var(--primary-color);
            transform: rotate(20deg);
            box-shadow: var(--shadow-md);
        }

        .btn-nav {
            padding: 11px 26px;
            font-size: 0.9rem;
            font-weight: 600;
            border-radius: var(--radius-md);
            transition: all var(--transition-base);
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }

        .btn-primary {
            background: var(--gradient-primary);
            color: white;
            box-shadow: var(--shadow-sm);
        }

        .btn-primary:hover {
            background: var(--primary-hover);
            transform: translateY(-2px);
            box-shadow: var(--shadow-md);
        }

        .btn-secondary {
            background: var(--bg-card);
            color: var(--primary-color);
            border: 2px solid var(--primary-color);
        }

        .btn-secondary:hover {
            background: var(--primary-color);
            color: white;
            transform: translateY(-2px);
        }

        .btn-admin {
            background: var(--gradient-secondary);
            color: white;
            box-shadow: var(--shadow-sm);
        }

        .btn-admin:hover {
            opacity: 0.95;
            transform: translateY(-2px);
            box-shadow: var(--shadow-md);
        }

        .btn-logout {
            background: var(--bg-card);
            color: var(--error-color);
            border: 2px solid var(--error-color);
        }

        .btn-logout:hover {
            background: var(--error-color);
            color: white;
        }

        /* Category Dropdown */
        .category-dropdown {
            position: relative;
        }

        .category-dropdown-btn {
            padding: 11px 20px;
            font-size: 0.9rem;
            font-weight: 600;
            background: var(--bg-card);
            border: 2px solid var(--border-color);
            border-radius: var(--radius-md);
            color: var(--text-primary);
            transition: all var(--transition-base);
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .category-dropdown-btn:hover {
            border-color: var(--primary-color);
        }

        .category-dropdown-btn i {
            transition: transform var(--transition-fast);
        }

        .category-dropdown.active .category-dropdown-btn i {
            transform: rotate(180deg);
        }

        .category-dropdown-menu {
            position: absolute;
            top: calc(100% + 10px);
            left: 0;
            min-width: 220px;
            max-height: 350px;
            overflow-y: auto;
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-lg);
            box-shadow: var(--shadow-xl);
            opacity: 0;
            visibility: hidden;
            transform: translateY(-10px);
            transition: all var(--transition-base);
            z-index: 100;
        }

        .category-dropdown.active .category-dropdown-menu {
            opacity: 1;
            visibility: visible;
            transform: translateY(0);
        }

        .category-dropdown-menu a {
            display: block;
            padding: 12px 18px;
            color: var(--text-primary);
            font-size: 0.9rem;
            transition: background var(--transition-fast);
            border-bottom: 1px solid var(--border-light);
        }

        .category-dropdown-menu a:last-child {
            border-bottom: none;
        }

        .category-dropdown-menu a:hover {
            background: var(--bg-badge);
            color: var(--primary-color);
        }

        /* Mobile Menu */
        .mobile-menu-btn {
            display: none;
            flex-direction: column;
            gap: 5px;
            padding: 10px;
            margin-left: auto;
        }

        .mobile-menu-btn span {
            width: 24px;
            height: 3px;
            background: var(--text-primary);
            border-radius: 2px;
            transition: all var(--transition-base);
        }

        .mobile-menu-btn.active span:nth-child(1) {
            transform: rotate(45deg) translate(6px, 6px);
        }

        .mobile-menu-btn.active span:nth-child(2) {
            opacity: 0;
        }

        .mobile-menu-btn.active span:nth-child(3) {
            transform: rotate(-45deg) translate(6px, -6px);
        }

        /* Mobile Nav */
        .mobile-nav {
            display: none;
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: var(--bg-header);
            padding: 20px;
            flex-direction: column;
            gap: 15px;
            box-shadow: var(--shadow-lg);
            border-top: 1px solid var(--border-color);
        }

        .mobile-nav.active {
            display: flex;
        }

        .mobile-nav .btn-nav {
            width: 100%;
            justify-content: center;
        }

        /* ==================== CONTAINER ==================== */
        .container {
            max-width: 1440px;
            margin: 0 auto;
            padding: 0 24px;
        }

        @media (min-width: 1600px) {
            .container {
                max-width: 1600px;
                padding: 0 40px;
            }
        }

        /* ==================== HERO SECTION ==================== */
        .hero-section {
            background: var(--gradient-hero);
            padding: 70px 0 90px;
            position: relative;
            overflow: hidden;
        }

        .hero-section::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.06'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
        }

        .hero-section::after {
            content: '';
            position: absolute;
            top: -50%;
            right: -10%;
            width: 500px;
            height: 500px;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
            border-radius: 50%;
        }

        .hero-content {
            position: relative;
            z-index: 1;
            text-align: center;
            color: white;
        }

        .hero-logo {
            width: 100px;
            height: 100px;
            background: rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(10px);
            border-radius: var(--radius-xl);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 3rem;
            margin: 0 auto 25px;
            animation: float 4s ease-in-out infinite;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }

        @keyframes float {
            0%, 100% { transform: translateY(0) rotate(0deg); }
            50% { transform: translateY(-15px) rotate(5deg); }
        }

        .hero-title {
            font-size: 3rem;
            font-weight: 800;
            margin-bottom: 15px;
            text-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            letter-spacing: -1px;
        }

        .hero-subtitle {
            font-size: 1.25rem;
            font-weight: 400;
            opacity: 0.95;
            margin-bottom: 35px;
            max-width: 600px;
            margin-left: auto;
            margin-right: auto;
        }

        .hero-cta-group {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
            flex-wrap: wrap;
        }

        .hero-cta {
            display: inline-flex;
            align-items: center;
            gap: 10px;
            padding: 16px 40px;
            font-size: 1.05rem;
            font-weight: 600;
            background: white;
            color: var(--primary-color);
            border-radius: var(--radius-full);
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.25);
            transition: all var(--transition-base);
        }

        .hero-cta:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.35);
        }

        .hero-cta i {
            transition: transform var(--transition-fast);
        }

        .hero-cta:hover i {
            transform: translateX(5px);
        }

        .hero-secondary {
            background: rgba(255,255,255,0.15);
            backdrop-filter: blur(10px);
            color: white;
            border: 2px solid rgba(255,255,255,0.3);
        }

        .hero-secondary:hover {
            background: rgba(255,255,255,0.25);
        }

        /* ==================== QUOTE SECTION ==================== */
        .quote-section {
            background: var(--bg-section);
            padding: 40px 0;
            border-bottom: 1px solid var(--border-light);
        }

        .quote-container {
            text-align: center;
        }

        .quote-wrapper {
            display: inline-flex;
            align-items: center;
            gap: 20px;
            padding: 20px 40px;
            background: var(--bg-badge);
            border-radius: var(--radius-full);
        }

        .quote-icon {
            font-size: 2rem;
            animation: bounce 2s infinite;
        }

        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-8px); }
        }

        .quote-text {
            font-size: 1.3rem;
            font-weight: 600;
            color: var(--text-primary);
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .quote-text .highlight {
            background: var(--gradient-primary);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: 700;
        }

        .sparkle {
            color: var(--accent-color);
            animation: sparkle 1.5s ease-in-out infinite;
        }

        @keyframes sparkle {
            0%, 100% { opacity: 1; transform: scale(1) rotate(0deg); }
            50% { opacity: 0.6; transform: scale(1.3) rotate(180deg); }
        }

        /* ==================== STATS BAR ==================== */
        .stats-section {
            padding: 40px 0;
        }

        .stats-bar {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 24px;
        }

        .stat-card {
            background: var(--bg-card);
            padding: 30px;
            border-radius: var(--radius-lg);
            text-align: center;
            box-shadow: var(--shadow-md);
            transition: all var(--transition-base);
            border: 1px solid var(--border-color);
            position: relative;
            overflow: hidden;
        }

        .stat-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: var(--gradient-primary);
            transform: scaleX(0);
            transition: transform var(--transition-base);
        }

        .stat-card:hover {
            transform: translateY(-8px);
            box-shadow: var(--shadow-xl);
        }

        .stat-card:hover::before {
            transform: scaleX(1);
        }

        .stat-icon {
            font-size: 3rem;
            margin-bottom: 15px;
            display: block;
        }

        .stat-number {
            font-size: 2.5rem;
            font-weight: 800;
            background: var(--gradient-primary);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            line-height: 1.2;
        }

        .stat-label {
            color: var(--text-secondary);
            font-size: 0.95rem;
            margin-top: 8px;
            font-weight: 500;
        }

        /* ==================== CATEGORY TABS ==================== */
        .category-tabs-section {
            padding: 20px 0;
        }

        .category-tabs {
            display: flex;
            gap: 12px;
            overflow-x: auto;
            padding: 10px 0;
            scrollbar-width: thin;
            scrollbar-color: var(--primary-color) var(--bg-card);
            -webkit-overflow-scrolling: touch;
        }

        .category-tabs::-webkit-scrollbar {
            height: 8px;
        }

        .category-tabs::-webkit-scrollbar-track {
            background: var(--bg-card);
            border-radius: var(--radius-full);
        }

        .category-tabs::-webkit-scrollbar-thumb {
            background: var(--gradient-primary);
            border-radius: var(--radius-full);
        }

        .category-tab {
            padding: 12px 28px;
            background: var(--bg-card);
            border: 2px solid var(--border-color);
            border-radius: var(--radius-full);
            font-size: 0.9rem;
            font-weight: 600;
            color: var(--text-secondary);
            white-space: nowrap;
            cursor: pointer;
            transition: all var(--transition-base);
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .category-tab:hover {
            border-color: var(--primary-color);
            color: var(--primary-color);
            transform: translateY(-2px);
            box-shadow: var(--shadow-md);
        }

        .category-tab.active {
            background: var(--gradient-primary);
            border-color: var(--primary-color);
            color: white;
            box-shadow: var(--shadow-glow);
        }

        /* ==================== SEARCH SECTION ==================== */
        .search-section {
            padding: 30px 0;
        }

        .search-row {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }

        .search-box-full {
            flex: 1;
            min-width: 280px;
            padding: 16px 24px;
            font-size: 1rem;
            background: var(--bg-card);
            border: 2px solid var(--border-color);
            border-radius: var(--radius-lg);
            color: var(--text-primary);
            outline: none;
            transition: all var(--transition-base);
            font-family: inherit;
        }

        .search-box-full:focus {
            border-color: var(--primary-color);
            box-shadow: var(--shadow-glow);
        }

        .search-box-full::placeholder {
            color: var(--text-muted);
        }

        .category-filter {
            min-width: 220px;
            padding: 16px 24px;
            font-size: 1rem;
            background: var(--bg-card);
            border: 2px solid var(--border-color);
            border-radius: var(--radius-lg);
            color: var(--text-primary);
            outline: none;
            cursor: pointer;
            transition: all var(--transition-base);
            font-family: inherit;
            appearance: none;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='%23626262' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
            background-repeat: no-repeat;
            background-position: right 12px center;
            background-size: 20px;
            padding-right: 45px;
        }

        .category-filter:focus {
            border-color: var(--primary-color);
        }

        /* ==================== SECTION HEADERS ==================== */
        .section-header {
            display: flex;
            align-items: center;
            gap: 16px;
            margin-bottom: 28px;
            position: relative;
        }

        .section-icon {
            width: 55px;
            height: 55px;
            background: var(--gradient-primary);
            border-radius: var(--radius-md);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.6rem;
            box-shadow: var(--shadow-md);
        }

        .section-title {
            font-size: 1.6rem;
            font-weight: 700;
            color: var(--text-primary);
            letter-spacing: -0.5px;
        }

        .section-subtitle {
            color: var(--text-secondary);
            font-size: 0.95rem;
            margin-left: auto;
        }

        /* ==================== TRENDING SECTION ==================== */
        .trending-section {
            background: var(--bg-section);
            padding: 50px 0;
            border-radius: var(--radius-xl);
            margin: 30px 0;
        }

        .trending-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 20px;
        }

        .trending-card {
            background: var(--bg-card);
            padding: 30px 20px;
            border-radius: var(--radius-lg);
            text-align: center;
            box-shadow: var(--shadow-md);
            transition: all var(--transition-base);
            border: 1px solid var(--border-color);
            cursor: pointer;
            position: relative;
            overflow: hidden;
        }

        .trending-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: var(--gradient-primary);
            opacity: 0;
            transition: opacity var(--transition-base);
        }

        .trending-card:hover {
            transform: translateY(-8px) scale(1.02);
            box-shadow: var(--shadow-xl);
        }

        .trending-card:hover::before {
            opacity: 0.05;
        }

        .trending-icon {
            font-size: 3.5rem;
            margin-bottom: 15px;
            display: block;
            position: relative;
            z-index: 1;
        }

        .trending-name {
            font-size: 1rem;
            font-weight: 600;
            color: var(--text-primary);
            position: relative;
            z-index: 1;
        }

        /* ==================== PRODUCTS GRID ==================== */
        .products-section {
            padding: 50px 0;
        }

        .category-section {
            margin-bottom: 50px;
            scroll-margin-top: 100px;
        }

        .products-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 24px;
        }

        .product-card {
            background: var(--bg-card);
            border-radius: var(--radius-lg);
            overflow: hidden;
            box-shadow: var(--shadow-sm);
            transition: all var(--transition-base);
            border: 1px solid var(--border-color);
            position: relative;
            display: block;
        }

        .product-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: var(--gradient-primary);
            transform: scaleX(0);
            transform-origin: left;
            transition: transform var(--transition-base);
            z-index: 10;
        }

        .product-card:hover {
            transform: translateY(-10px);
            box-shadow: var(--shadow-xl);
            border-color: var(--primary-color);
        }

        .product-card:hover::before {
            transform: scaleX(1);
        }

        .product-card-body {
            padding: 24px;
        }

        .product-logo {
            width: 70px;
            height: 70px;
            background: var(--gradient-hero);
            border-radius: var(--radius-md);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2rem;
            margin-bottom: 18px;
            box-shadow: var(--shadow-md);
        }

        .product-name {
            font-size: 1.1rem;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 10px;
            line-height: 1.4;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }

        .product-category {
            font-size: 0.8rem;
            color: var(--text-secondary);
            background: var(--bg-badge);
            padding: 6px 14px;
            border-radius: var(--radius-full);
            display: inline-block;
            margin-bottom: 18px;
            font-weight: 500;
        }

        .product-btn {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            width: 100%;
            padding: 14px;
            font-size: 0.95rem;
            font-weight: 600;
            background: var(--gradient-primary);
            color: white;
            border-radius: var(--radius-md);
            transition: all var(--transition-base);
        }

        .product-btn:hover {
            background: var(--primary-hover);
            transform: scale(1.03);
            box-shadow: var(--shadow-md);
        }

        .product-btn i {
            transition: transform var(--transition-fast);
        }

        .product-btn:hover i {
            transform: translateX(4px);
        }

        /* Badges */
        .badge {
            position: absolute;
            top: 14px;
            right: 14px;
            padding: 6px 14px;
            font-size: 0.7rem;
            font-weight: 700;
            border-radius: var(--radius-full);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            z-index: 5;
            display: flex;
            align-items: center;
            gap: 4px;
        }

        .badge-popular {
            background: var(--gradient-secondary);
            color: white;
        }

        .badge-new {
            background: var(--gradient-success);
            color: white;
        }

        .badge-trending {
            background: var(--gradient-gold);
            color: #172337;
        }

        /* ==================== FLASH MESSAGES ==================== */
        .flash-messages {
            max-width: 1440px;
            margin: 20px auto;
            padding: 0 24px;
            position: relative;
            z-index: 999;
        }

        .flash {
            padding: 16px 24px;
            border-radius: var(--radius-md);
            margin-bottom: 15px;
            animation: slideDown 0.4s ease, fadeOut 0.4s ease 4.6s forwards;
            display: flex;
            align-items: center;
            gap: 12px;
            font-weight: 500;
            box-shadow: var(--shadow-md);
        }

        @keyframes slideDown {
            from {
                opacity: 0;
                transform: translateY(-20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes fadeOut {
            to {
                opacity: 0;
                transform: translateY(-10px);
            }
        }

        .flash.success {
            background: rgba(16, 185, 129, 0.15);
            border: 1px solid var(--success-color);
            color: var(--success-color);
        }

        .flash.error {
            background: rgba(239, 68, 68, 0.15);
            border: 1px solid var(--error-color);
            color: var(--error-color);
        }

        /* ==================== AUTH CONTAINER ==================== */
        .auth-container {
            max-width: 500px;
            margin: 60px auto;
            padding: 50px;
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-xl);
            box-shadow: var(--shadow-lg);
        }

        .auth-title {
            font-size: 2rem;
            text-align: center;
            margin-bottom: 35px;
            color: var(--text-primary);
            font-weight: 700;
        }

        .auth-tabs {
            display: flex;
            gap: 12px;
            margin-bottom: 30px;
            background: var(--bg-body);
            padding: 6px;
            border-radius: var(--radius-lg);
        }

        .auth-tab {
            flex: 1;
            padding: 14px;
            font-size: 0.95rem;
            font-weight: 600;
            background: transparent;
            border: none;
            border-radius: var(--radius-md);
            color: var(--text-secondary);
            cursor: pointer;
            transition: all var(--transition-base);
        }

        .auth-tab.active {
            background: var(--gradient-primary);
            color: white;
            box-shadow: var(--shadow-sm);
        }

        .form-group {
            margin-bottom: 24px;
        }

        .form-group label {
            display: block;
            margin-bottom: 10px;
            color: var(--text-secondary);
            font-size: 0.9rem;
            font-weight: 500;
        }

        .form-group input,
        .form-group select {
            width: 100%;
            padding: 15px 18px;
            font-size: 1rem;
            background: var(--bg-input);
            border: 2px solid var(--border-color);
            border-radius: var(--radius-md);
            color: var(--text-primary);
            outline: none;
            transition: all var(--transition-base);
            font-family: inherit;
        }

        .form-group input:focus,
        .form-group select:focus {
            border-color: var(--primary-color);
            box-shadow: var(--shadow-glow);
        }

        .btn-submit {
            width: 100%;
            padding: 16px;
            font-size: 1rem;
            font-weight: 600;
            background: var(--gradient-primary);
            border: none;
            border-radius: var(--radius-md);
            color: white;
            cursor: pointer;
            transition: all var(--transition-base);
            margin-top: 10px;
        }

        .btn-submit:hover {
            background: var(--primary-hover);
            transform: translateY(-3px);
            box-shadow: var(--shadow-lg);
        }

        .auth-switch {
            text-align: center;
            margin-top: 28px;
            color: var(--text-secondary);
            font-size: 0.95rem;
        }

        .auth-switch a {
            color: var(--primary-color);
            font-weight: 600;
        }

        .auth-switch a:hover {
            text-decoration: underline;
        }

        /* ==================== ADMIN PANEL ==================== */
        .admin-panel {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-xl);
            padding: 40px;
            margin-bottom: 30px;
            box-shadow: var(--shadow-md);
        }

        .admin-title {
            font-size: 1.7rem;
            color: var(--primary-color);
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 25px;
        }

        .admin-form {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr auto;
            gap: 15px;
            align-items: end;
        }

        .admin-form .form-group {
            margin-bottom: 0;
        }

        .admin-form input,
        .admin-form select {
            width: 100%;
            padding: 14px 18px;
            font-size: 0.95rem;
            background: var(--bg-input);
            border: 2px solid var(--border-color);
            border-radius: var(--radius-md);
            color: var(--text-primary);
            outline: none;
            font-family: inherit;
        }

        .admin-form input:focus,
        .admin-form select:focus {
            border-color: var(--primary-color);
        }

        .btn-add {
            padding: 14px 30px;
            font-size: 0.95rem;
            font-weight: 600;
            background: var(--gradient-success);
            border: none;
            border-radius: var(--radius-md);
            color: white;
            cursor: pointer;
            transition: all var(--transition-base);
            white-space: nowrap;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }

        .btn-add:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-md);
        }

        .websites-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 25px;
            background: var(--bg-card);
            border-radius: var(--radius-md);
            overflow: hidden;
        }

        .websites-table th,
        .websites-table td {
            padding: 16px;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }

        .websites-table th {
            background: var(--bg-body);
            color: var(--text-secondary);
            font-weight: 600;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .websites-table td {
            color: var(--text-primary);
            font-size: 0.95rem;
        }

        .websites-table tr:hover {
            background: var(--bg-card-hover);
        }

        .btn-delete {
            padding: 9px 20px;
            font-size: 0.85rem;
            font-weight: 600;
            background: var(--gradient-secondary);
            border: none;
            border-radius: var(--radius-md);
            color: white;
            cursor: pointer;
            transition: all var(--transition-base);
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }

        .btn-delete:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-md);
        }

        /* ==================== FOOTER ==================== */
        .footer {
            background: var(--bg-footer);
            color: var(--text-light);
            padding: 70px 0 35px;
            margin-top: 80px;
        }

        .footer-content {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 45px;
            margin-bottom: 50px;
        }

        .footer-section h3 {
            font-size: 1.3rem;
            margin-bottom: 25px;
            color: white;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .footer-section p {
            color: rgba(255, 255, 255, 0.7);
            line-height: 1.9;
            font-size: 0.95rem;
        }

        .footer-links {
            list-style: none;
        }

        .footer-links li {
            margin-bottom: 14px;
        }

        .footer-links a {
            color: rgba(255, 255, 255, 0.7);
            font-size: 0.95rem;
            transition: all var(--transition-fast);
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }

        .footer-links a:hover {
            color: white;
            transform: translateX(5px);
        }

        .footer-social {
            display: flex;
            gap: 12px;
            margin-top: 25px;
        }

        .footer-social a {
            width: 48px;
            height: 48px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: var(--radius-md);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.3rem;
            transition: all var(--transition-base);
        }

        .footer-social a:hover {
            background: var(--primary-color);
            transform: translateY(-5px);
        }

        .footer-bottom {
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            padding-top: 30px;
            text-align: center;
            color: rgba(255, 255, 255, 0.5);
            font-size: 0.9rem;
        }

        .footer-bottom a {
            color: var(--primary-color);
            font-weight: 500;
        }

        /* ==================== LOADING SKELETON ==================== */
        .skeleton {
            background: linear-gradient(90deg, var(--bg-card) 25%, var(--bg-card-hover) 50%, var(--bg-card) 75%);
            background-size: 200% 100%;
            animation: skeleton-loading 1.5s infinite;
            border-radius: var(--radius-md);
        }

        @keyframes skeleton-loading {
            0% { background-position: 200% 0; }
            100% { background-position: -200% 0; }
        }

        .skeleton-card {
            padding: 24px;
        }

        .skeleton-logo {
            width: 70px;
            height: 70px;
            margin-bottom: 18px;
        }

        .skeleton-title {
            height: 20px;
            width: 80%;
            margin-bottom: 10px;
        }

        .skeleton-category {
            height: 24px;
            width: 100px;
            margin-bottom: 18px;
            border-radius: var(--radius-full);
        }

        .skeleton-button {
            height: 44px;
            width: 100%;
            border-radius: var(--radius-md);
        }

        /* ==================== NO RESULTS ==================== */
        .no-results {
            text-align: center;
            padding: 100px 20px;
            color: var(--text-secondary);
        }

        .no-results-icon {
            font-size: 5rem;
            margin-bottom: 25px;
            opacity: 0.4;
        }

        .no-results-text {
            font-size: 1.3rem;
            margin-bottom: 10px;
        }

        .no-results-sub {
            color: var(--text-muted);
            font-size: 1rem;
        }

        /* ==================== SCROLL TO TOP ==================== */
        .scroll-to-top {
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 50px;
            height: 50px;
            background: var(--gradient-primary);
            border-radius: var(--radius-full);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.3rem;
            color: white;
            box-shadow: var(--shadow-lg);
            cursor: pointer;
            opacity: 0;
            visibility: hidden;
            transform: translateY(20px);
            transition: all var(--transition-base);
            z-index: 999;
        }

        .scroll-to-top.visible {
            opacity: 1;
            visibility: visible;
            transform: translateY(0);
        }

        .scroll-to-top:hover {
            transform: translateY(-5px);
            box-shadow: var(--shadow-xl);
        }

        /* ==================== RESPONSIVE ==================== */
        @media (max-width: 1024px) {
            .header-main .container {
                flex-wrap: wrap;
            }

            .search-container {
                order: 3;
                max-width: 100%;
                width: 100%;
                margin-top: 15px;
            }

            .products-grid {
                grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
            }

            .admin-form {
                grid-template-columns: 1fr 1fr;
            }
        }

        @media (max-width: 768px) {
            .header-top {
                display: none;
            }

            .header-main .container {
                flex-wrap: nowrap;
            }

            .mobile-menu-btn {
                display: flex;
            }

            .nav-actions {
                display: none;
            }

            .hero-title {
                font-size: 2.2rem;
            }

            .hero-subtitle {
                font-size: 1.05rem;
            }

            .quote-text {
                font-size: 1.1rem;
            }

            .quote-wrapper {
                padding: 15px 25px;
            }

            .auth-container {
                margin: 40px auto;
                padding: 35px 28px;
            }

            .admin-form {
                grid-template-columns: 1fr;
            }

            .products-grid {
                grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
                gap: 16px;
            }

            .stat-card {
                padding: 24px 20px;
            }

            .stat-number {
                font-size: 2rem;
            }

            .footer-content {
                grid-template-columns: 1fr;
                gap: 35px;
            }

            .section-title {
                font-size: 1.3rem;
            }

            .trending-grid {
                grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            }
        }

        @media (max-width: 480px) {
            .logo-text .tagline {
                display: none;
            }

            .products-grid {
                grid-template-columns: 1fr;
            }

            .stat-card {
                width: 100%;
            }

            .auth-title {
                font-size: 1.6rem;
            }

            .hero-logo {
                width: 80px;
                height: 80px;
                font-size: 2.5rem;
            }

            .hero-cta-group {
                flex-direction: column;
            }

            .hero-cta {
                width: 100%;
                justify-content: center;
            }
        }

        /* ==================== UTILITY CLASSES ==================== */
        .text-center { text-align: center; }
        .text-primary { color: var(--primary-color); }
        .text-secondary { color: var(--text-secondary); }
        .text-muted { color: var(--text-muted); }
        .mt-1 { margin-top: 10px; }
        .mt-2 { margin-top: 20px; }
        .mt-3 { margin-top: 30px; }
        .mb-1 { margin-bottom: 10px; }
        .mb-2 { margin-bottom: 20px; }
        .mb-3 { margin-bottom: 30px; }
    </style>
</head>
<body>
    <!-- Premium Header -->
    <header class="sticky-header" id="stickyHeader">
        <div class="header-top">
            <div class="container">
                <div class="top-announcement">
                    <i class="fas fa-bullhorn"></i>
                    <span>Welcome to India's Largest Shopping Link Directory</span>
                </div>
                <div class="top-links">
                    {% if session.get('user_id') %}
                        <span><i class="fas fa-user-circle"></i> {{ session.get('username') }}</span>
                        {% if session.get('is_admin') %}
                            <a href="{{ url_for('admin') }}"><i class="fas fa-crown"></i> Admin Panel</a>
                        {% endif %}
                        <a href="{{ url_for('logout') }}"><i class="fas fa-sign-out-alt"></i> Logout</a>
                    {% else %}
                        <a href="{{ url_for('login') }}"><i class="fas fa-sign-in-alt"></i> Login</a>
                        <a href="{{ url_for('signup') }}"><i class="fas fa-user-plus"></i> Sign Up</a>
                    {% endif %}
                </div>
            </div>
        </div>
        <div class="header-main">
            <div class="container">
                <a href="{{ url_for('index') }}" class="logo">
                    <div class="logo-icon">🛒</div>
                    <div class="logo-text">
                        <span class="brand">App Linker</span>
                        <span class="tagline">Links 285+ sites in one</span>
                    </div>
                </a>

                <div class="search-container">
                    <div class="search-box-wrapper">
                        <input type="text" class="search-box" id="headerSearch" placeholder="🔍 Search for websites, categories...">
                        <button class="search-btn" onclick="scrollToSearch()">
                            <i class="fas fa-search"></i>
                        </button>
                    </div>
                </div>

                <div class="nav-actions" id="navActions">
                    <!-- Category Dropdown -->
                    <div class="category-dropdown" id="categoryDropdown">
                        <button class="category-dropdown-btn" onclick="toggleCategoryDropdown()">
                            <i class="fas fa-th-large"></i> Categories
                            <i class="fas fa-chevron-down"></i>
                        </button>
                        <div class="category-dropdown-menu" id="categoryDropdownMenu">
                            <a href="#" onclick="filterByCategory(''); return false;">All Categories</a>
                            <a href="#" onclick="filterByCategory('General Shopping'); return false;">General Shopping</a>
                            <a href="#" onclick="filterByCategory('Fashion & Clothing'); return false;">Fashion & Clothing</a>
                            <a href="#" onclick="filterByCategory('Electronics'); return false;">Electronics</a>
                            <a href="#" onclick="filterByCategory('Beauty & Personal Care'); return false;">Beauty & Personal Care</a>
                            <a href="#" onclick="filterByCategory('Grocery & Daily Needs'); return false;">Grocery & Daily Needs</a>
                            <a href="#" onclick="filterByCategory('Furniture & Home'); return false;">Furniture & Home</a>
                            <a href="#" onclick="filterByCategory('Health & Pharmacy'); return false;">Health & Pharmacy</a>
                            <a href="#" onclick="filterByCategory('Food Delivery'); return false;">Food Delivery</a>
                            <a href="#" onclick="filterByCategory('Travel'); return false;">Travel</a>
                        </div>
                    </div>

                    <button class="theme-toggle" onclick="toggleTheme()" title="Toggle Dark/Light Mode">
                        <span id="themeIcon">🌙</span>
                    </button>
                    {% if not session.get('user_id') %}
                        <a href="{{ url_for('login') }}" class="btn-nav btn-primary">
                            <i class="fas fa-sign-in-alt"></i> Login
                        </a>
                        <a href="{{ url_for('signup') }}" class="btn-nav btn-secondary">
                            <i class="fas fa-user-plus"></i> Sign Up
                        </a>
                    {% else %}
                        <a href="{{ url_for('user_history') }}" class="btn-nav btn-secondary">
                            <i class="fas fa-history"></i> My History
                        </a>
                        {% if session.get('is_admin') %}
                            <a href="{{ url_for('admin') }}" class="btn-nav btn-admin">
                                <i class="fas fa-crown"></i> Admin
                            </a>
                        {% endif %}
                        <a href="{{ url_for('logout') }}" class="btn-nav btn-logout">
                            <i class="fas fa-sign-out-alt"></i> Logout
                        </a>
                    {% endif %}
                </div>

                <button class="mobile-menu-btn" onclick="toggleMobileMenu()">
                    <span></span>
                    <span></span>
                    <span></span>
                </button>
            </div>
        </div>

        <!-- Mobile Navigation -->
        <div class="mobile-nav" id="mobileNav">
            <a href="{{ url_for('index') }}" class="btn-nav btn-primary" style="justify-content: center;">
                <i class="fas fa-home"></i> Home
            </a>
            {% if not session.get('user_id') %}
                <a href="{{ url_for('login') }}" class="btn-nav btn-primary" style="justify-content: center;">
                    <i class="fas fa-sign-in-alt"></i> Login
                </a>
                <a href="{{ url_for('signup') }}" class="btn-nav btn-secondary" style="justify-content: center;">
                    <i class="fas fa-user-plus"></i> Sign Up
                </a>
            {% else %}
                <a href="{{ url_for('user_history') }}" class="btn-nav btn-secondary" style="justify-content: center;">
                    <i class="fas fa-history"></i> My History
                </a>
                {% if session.get('is_admin') %}
                    <a href="{{ url_for('admin') }}" class="btn-nav btn-admin" style="justify-content: center;">
                        <i class="fas fa-crown"></i> Admin Panel
                    </a>
                {% endif %}
                <a href="{{ url_for('logout') }}" class="btn-nav btn-logout" style="justify-content: center;">
                    <i class="fas fa-sign-out-alt"></i> Logout
                </a>
            {% endif %}
            <button class="btn-nav btn-secondary" onclick="toggleTheme()" style="justify-content: center; width: 100%;">
                <span id="mobileThemeIcon">🌙</span> Toggle Theme
            </button>
        </div>
    </header>

    <!-- Flash Messages -->
    <div class="flash-messages">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="flash {{ category }}">
                        <i class="fas {% if category == 'success' %}fa-check-circle{% else %}fa-exclamation-circle{% endif %}"></i>
                        {{ message }}
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
    </div>

    <!-- Main Content -->
    <main>
        {% block content %}{% endblock %}
    </main>

    <!-- Footer -->
    <footer class="footer">
        <div class="container">
            <div class="footer-content">
                <div class="footer-section">
                    <h3><i class="fas fa-shopping-bag"></i> App Linker</h3>
                    <p>Your one-stop destination to discover and access 285+ shopping websites across all categories. We make online shopping easier by bringing all your favorite stores together in one place.</p>
                    <div class="footer-social">
                        <a href="#" title="Facebook"><i class="fab fa-facebook-f"></i></a>
                        <a href="#" title="Twitter"><i class="fab fa-twitter"></i></a>
                        <a href="#" title="Instagram"><i class="fab fa-instagram"></i></a>
                        <a href="#" title="LinkedIn"><i class="fab fa-linkedin-in"></i></a>
                        <a href="#" title="YouTube"><i class="fab fa-youtube"></i></a>
                    </div>
                </div>
                <div class="footer-section">
                    <h3><i class="fas fa-bolt"></i> Quick Links</h3>
                    <ul class="footer-links">
                        <li><a href="{{ url_for('index') }}"><i class="fas fa-chevron-right"></i> Home</a></li>
                        <li><a href="#trending"><i class="fas fa-chevron-right"></i> Trending Sites</a></li>
                        <li><a href="#categories"><i class="fas fa-chevron-right"></i> All Categories</a></li>
                        <li><a href="{{ url_for('login') }}"><i class="fas fa-chevron-right"></i> Login</a></li>
                        <li><a href="{{ url_for('signup') }}"><i class="fas fa-chevron-right"></i> Sign Up</a></li>
                    </ul>
                </div>
                <div class="footer-section">
                    <h3><i class="fas fa-tags"></i> Top Categories</h3>
                    <ul class="footer-links">
                        <li><a href="#" onclick="filterByCategory('General Shopping'); return false;"><i class="fas fa-chevron-right"></i> General Shopping</a></li>
                        <li><a href="#" onclick="filterByCategory('Fashion & Clothing'); return false;"><i class="fas fa-chevron-right"></i> Fashion & Clothing</a></li>
                        <li><a href="#" onclick="filterByCategory('Electronics'); return false;"><i class="fas fa-chevron-right"></i> Electronics</a></li>
                        <li><a href="#" onclick="filterByCategory('Beauty & Personal Care'); return false;"><i class="fas fa-chevron-right"></i> Beauty & Personal Care</a></li>
                        <li><a href="#" onclick="filterByCategory('Grocery & Daily Needs'); return false;"><i class="fas fa-chevron-right"></i> Grocery & Daily Needs</a></li>
                    </ul>
                </div>
                <div class="footer-section">
                    <h3><i class="fas fa-headset"></i> Support</h3>
                    <ul class="footer-links">
                        <li><a href="#"><i class="fas fa-chevron-right"></i> About Us</a></li>
                        <li><a href="#"><i class="fas fa-chevron-right"></i> Contact</a></li>
                        <li><a href="#"><i class="fas fa-chevron-right"></i> Privacy Policy</a></li>
                        <li><a href="#"><i class="fas fa-chevron-right"></i> Terms of Service</a></li>
                        <li><a href="#"><i class="fas fa-chevron-right"></i> FAQ</a></li>
                    </ul>
                </div>
            </div>
            <div class="footer-bottom">
                <p>&copy; 2026 <a href="#">App Linker</a>. All rights reserved. | Made with <i class="fas fa-heart" style="color: #ef4444;"></i> for Online Shoppers</p>
            </div>
        </div>
    </footer>

    <!-- Scroll to Top Button -->
    <div class="scroll-to-top" id="scrollToTop" onclick="scrollToTop()">
        <i class="fas fa-chevron-up"></i>
    </div>

    <script>
        // ==================== THEME TOGGLE ====================
        function initTheme() {
            const savedTheme = localStorage.getItem('theme') || 'light';
            document.documentElement.setAttribute('data-theme', savedTheme);
            updateThemeIcon(savedTheme);
        }

        function toggleTheme() {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateThemeIcon(newTheme);
        }

        function updateThemeIcon(theme) {
            const icon = document.getElementById('themeIcon');
            const mobileIcon = document.getElementById('mobileThemeIcon');
            const emoji = theme === 'dark' ? '☀️' : '🌙';
            if (icon) icon.textContent = emoji;
            if (mobileIcon) mobileIcon.textContent = emoji;
        }

        // ==================== MOBILE MENU ====================
        function toggleMobileMenu() {
            const btn = document.querySelector('.mobile-menu-btn');
            const nav = document.getElementById('mobileNav');
            btn.classList.toggle('active');
            nav.classList.toggle('active');
        }

        // ==================== CATEGORY DROPDOWN ====================
        function toggleCategoryDropdown() {
            const dropdown = document.getElementById('categoryDropdown');
            dropdown.classList.toggle('active');
        }

        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            const dropdown = document.getElementById('categoryDropdown');
            if (dropdown && !dropdown.contains(e.target)) {
                dropdown.classList.remove('active');
            }
        });

        // ==================== SCROLL TO SEARCH ====================
        function scrollToSearch() {
            const searchBox = document.getElementById('searchBox');
            if (searchBox) {
                searchBox.scrollIntoView({ behavior: 'smooth', block: 'center' });
                searchBox.focus();
            }
        }

        // ==================== SCROLL TO TOP ====================
        function scrollToTop() {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }

        // Show/hide scroll to top button
        window.addEventListener('scroll', function() {
            const scrollBtn = document.getElementById('scrollToTop');
            const header = document.getElementById('stickyHeader');
            if (scrollBtn) {
                if (window.scrollY > 400) {
                    scrollBtn.classList.add('visible');
                } else {
                    scrollBtn.classList.remove('visible');
                }
            }
            if (header) {
                if (window.scrollY > 50) {
                    header.classList.add('scrolled');
                } else {
                    header.classList.remove('scrolled');
                }
            }
        });

        // ==================== CATEGORY FILTER ====================
        function filterByCategory(category) {
            const filter = document.getElementById('categoryFilter');
            if (filter) {
                filter.value = category;
                filter.dispatchEvent(new Event('change'));
            }
            document.querySelectorAll('.category-tab').forEach(tab => {
                tab.classList.remove('active');
            });
            event.target.closest('.category-tab')?.classList.add('active');
            
            // Close dropdown
            document.getElementById('categoryDropdown')?.classList.remove('active');
            
            // Scroll to products section
            const productsSection = document.getElementById('products');
            if (productsSection) {
                productsSection.scrollIntoView({ behavior: 'smooth' });
            }
        }

        // Initialize theme on load
        initTheme();
    </script>

    <!-- Floating Remarks/Feedback Button -->
    <button id="remarksBtn" class="remarks-float-btn" onclick="openRemarksModal()" title="Submit Feedback">
        <i class="fas fa-comment-dots"></i>
        <span>Feedback</span>
    </button>

    <!-- Remarks Modal -->
    <div id="remarksModal" class="remarks-modal">
        <div class="remarks-modal-content">
            <div class="remarks-modal-header">
                <h3><i class="fas fa-comment-dots"></i> Submit Your Feedback</h3>
                <button class="remarks-modal-close" onclick="closeRemarksModal()">&times;</button>
            </div>
            <form action="/submit_remark" method="POST">
                <div class="form-group">
                    <label for="remarkName"><i class="fas fa-user"></i> Your Name (Optional)</label>
                    <input type="text" id="remarkName" name="name" placeholder="Enter your name">
                </div>
                <div class="form-group">
                    <label for="remarkMessage"><i class="fas fa-comment"></i> Your Message</label>
                    <textarea id="remarkMessage" name="message" rows="5" required placeholder="Share your thoughts, suggestions, or feedback..."></textarea>
                </div>
                <div class="remarks-modal-footer">
                    <button type="button" class="btn-cancel" onclick="closeRemarksModal()">Cancel</button>
                    <button type="submit" class="btn-submit-remark"><i class="fas fa-paper-plane"></i> Submit Feedback</button>
                </div>
            </form>
        </div>
    </div>

    <style>
        /* Floating Remarks Button */
        .remarks-float-btn {
            position: fixed;
            bottom: 25px;
            right: 25px;
            z-index: 9998;
            background: var(--gradient-primary);
            color: white;
            border: none;
            border-radius: 50px;
            padding: 14px 24px;
            font-size: 0.95rem;
            font-weight: 600;
            cursor: pointer;
            box-shadow: var(--shadow-lg);
            display: flex;
            align-items: center;
            gap: 10px;
            transition: all var(--transition-base);
        }

        .remarks-float-btn:hover {
            transform: translateY(-4px);
            box-shadow: var(--shadow-xl);
        }

        .remarks-float-btn i {
            font-size: 1.2rem;
        }

        /* Remarks Modal */
        .remarks-modal {
            display: none;
            position: fixed;
            z-index: 9999;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.7);
            backdrop-filter: blur(4px);
            animation: fadeIn 0.3s ease;
        }

        .remarks-modal.active {
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .remarks-modal-content {
            background: var(--bg-card);
            border-radius: var(--radius-lg);
            width: 90%;
            max-width: 500px;
            max-height: 80vh;
            overflow-y: auto;
            box-shadow: var(--shadow-xl);
            animation: slideUp 0.3s ease;
        }

        .remarks-modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px 25px;
            border-bottom: 1px solid var(--border-color);
        }

        .remarks-modal-header h3 {
            color: var(--primary-color);
            font-size: 1.3rem;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .remarks-modal-close {
            background: none;
            border: none;
            font-size: 1.8rem;
            color: var(--text-secondary);
            cursor: pointer;
            transition: color var(--transition-fast);
        }

        .remarks-modal-close:hover {
            color: var(--error-color);
        }

        .remarks-modal-content .form-group {
            padding: 20px 25px;
        }

        .remarks-modal-content label {
            display: block;
            color: var(--text-secondary);
            font-size: 0.9rem;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .remarks-modal-content input,
        .remarks-modal-content textarea {
            width: 100%;
            padding: 12px 16px;
            font-size: 1rem;
            background: var(--bg-input);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-md);
            color: var(--text-primary);
            outline: none;
            transition: all var(--transition-base);
            font-family: inherit;
        }

        .remarks-modal-content input:focus,
        .remarks-modal-content textarea:focus {
            border-color: var(--primary-color);
            box-shadow: 0 0 0 3px rgba(40, 116, 240, 0.1);
        }

        .remarks-modal-content textarea {
            resize: vertical;
            min-height: 120px;
        }

        .remarks-modal-footer {
            display: flex;
            gap: 12px;
            justify-content: flex-end;
            padding: 20px 25px;
            border-top: 1px solid var(--border-color);
        }

        .btn-cancel {
            padding: 12px 24px;
            font-size: 0.95rem;
            font-weight: 600;
            background: var(--bg-input);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-md);
            color: var(--text-secondary);
            cursor: pointer;
            transition: all var(--transition-base);
        }

        .btn-cancel:hover {
            background: var(--bg-card-hover);
            color: var(--text-primary);
        }

        .btn-submit-remark {
            padding: 12px 24px;
            font-size: 0.95rem;
            font-weight: 600;
            background: var(--gradient-primary);
            border: none;
            border-radius: var(--radius-md);
            color: white;
            cursor: pointer;
            transition: all var(--transition-base);
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .btn-submit-remark:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-md);
        }

        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        @keyframes slideUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @media (max-width: 768px) {
            .remarks-float-btn {
                bottom: 15px;
                right: 15px;
                padding: 12px 18px;
            }

            .remarks-float-btn span {
                display: none;
            }

            .remarks-modal-content {
                width: 95%;
                margin: 20px auto;
            }
        }
    </style>

    <script>
        // Remarks Modal Functions
        function openRemarksModal() {
            document.getElementById('remarksModal').classList.add('active');
        }

        function closeRemarksModal() {
            document.getElementById('remarksModal').classList.remove('active');
        }

        // Close modal when clicking outside
        document.getElementById('remarksModal')?.addEventListener('click', function(e) {
            if (e.target === this) {
                closeRemarksModal();
            }
        });
    </script>

    {% block scripts %}{% endblock %}
</body>
</html>
'''

# ============================================================================
# INDEX TEMPLATE - PREMIUM E-COMMERCE STYLE
# ============================================================================
INDEX_TEMPLATE = '''
{% extends "base" %}
{% block content %}
<!-- Hero Section -->
<section class="hero-section">
    <div class="container">
        <div class="hero-content">
            <div class="hero-logo">🛒</div>
            <h1 class="hero-title">Welcome to App Linker</h1>
            <p class="hero-subtitle">Your Ultimate Shopping Destination - Discover and access 285+ premium shopping websites across all categories in one place</p>
            <div class="hero-cta-group">
                <a href="#products" class="hero-cta">
                    <i class="fas fa-rocket"></i> Explore Now
                </a>
                <a href="#trending" class="hero-cta hero-secondary">
                    <i class="fas fa-fire"></i> Trending Sites
                </a>
            </div>
        </div>
    </div>
</section>

<!-- Quote Section -->
<section class="quote-section">
    <div class="container">
        <div class="quote-container">
            <div class="quote-wrapper">
                <span class="quote-icon">✨</span>
                <p class="quote-text">
                    <span class="highlight">Links 285+ sites</span> in one place - Your Shopping Made Easy!
                    <span class="sparkle">⭐</span>
                </p>
            </div>
        </div>
    </div>
</section>

<!-- Stats Section -->
<section class="stats-section">
    <div class="container">
        <div class="stats-bar">
            <div class="stat-card">
                <span class="stat-icon">🌐</span>
                <div class="stat-number">{{ total_websites }}</div>
                <div class="stat-label">Websites Listed</div>
            </div>
            <div class="stat-card">
                <span class="stat-icon">📂</span>
                <div class="stat-number">{{ total_categories }}</div>
                <div class="stat-label">Categories</div>
            </div>
            <div class="stat-card">
                <span class="stat-icon">🛍️</span>
                <div class="stat-number">285+</div>
                <div class="stat-label">Shopping Sites</div>
            </div>
            <div class="stat-card">
                <span class="stat-icon">👥</span>
                <div class="stat-number">1000+</div>
                <div class="stat-label">Happy Users</div>
            </div>
        </div>
    </div>
</section>

<!-- Category Tabs -->
<section class="category-tabs-section">
    <div class="container">
        <div class="category-tabs" id="categories">
            <button class="category-tab active" onclick="filterByCategory('')">
                <i class="fas fa-th"></i> All Categories
            </button>
            {% for category in categories[:12] %}
            <button class="category-tab" onclick="filterByCategory('{{ category }}')">
                <i class="fas fa-tag"></i> {{ category }}
            </button>
            {% endfor %}
        </div>
    </div>
</section>

<!-- Search Section -->
<section class="search-section">
    <div class="container">
        <div class="search-row">
            <input type="text" class="search-box-full" id="searchBox" placeholder="🔍 Search websites by name...">
            <select class="category-filter" id="categoryFilter" onchange="filterWebsites()">
                <option value="">All Categories</option>
                {% for category in categories %}
                <option value="{{ category }}">{{ category }}</option>
                {% endfor %}
            </select>
        </div>
    </div>
</section>

<!-- Trending Section -->
<section class="trending-section" id="trending">
    <div class="container">
        <div class="section-header">
            <div class="section-icon"><i class="fas fa-fire" style="color: white;"></i></div>
            <h2 class="section-title">Trending Categories</h2>
            <span class="section-subtitle">Most popular this week</span>
        </div>
        <div class="trending-grid">
            <div class="trending-card" onclick="filterByCategory('General Shopping')">
                <span class="trending-icon">🛒</span>
                <span class="trending-name">General Shopping</span>
            </div>
            <div class="trending-card" onclick="filterByCategory('Fashion & Clothing')">
                <span class="trending-icon">👕</span>
                <span class="trending-name">Fashion</span>
            </div>
            <div class="trending-card" onclick="filterByCategory('Electronics')">
                <span class="trending-icon">📱</span>
                <span class="trending-name">Electronics</span>
            </div>
            <div class="trending-card" onclick="filterByCategory('Beauty & Personal Care')">
                <span class="trending-icon">💄</span>
                <span class="trending-name">Beauty</span>
            </div>
            <div class="trending-card" onclick="filterByCategory('Grocery & Daily Needs')">
                <span class="trending-icon">🥬</span>
                <span class="trending-name">Grocery</span>
            </div>
            <div class="trending-card" onclick="filterByCategory('Health & Pharmacy')">
                <span class="trending-icon">💊</span>
                <span class="trending-name">Health</span>
            </div>
        </div>
    </div>
</section>

<!-- Products Section -->
<section class="products-section" id="products">
    <div class="container">
        {% for category, websites in websites_by_category.items() %}
        <div class="category-section" data-category="{{ category }}">
            <div class="section-header">
                <div class="section-icon"><i class="fas fa-store" style="color: white;"></i></div>
                <h2 class="section-title">{{ category }}</h2>
                <span class="section-subtitle">{{ websites|length }} sites</span>
            </div>
            <div class="products-grid">
                {% for website in websites %}
                <a href="/visit/{{ website.name | urlencode }}" target="_blank" class="product-card" data-name="{{ website.name|lower }}" data-category="{{ category }}">
                    {% if loop.index <= 3 %}
                    <span class="badge badge-popular">
                        <i class="fas fa-fire"></i> Popular
                    </span>
                    {% elif loop.index <= 5 %}
                    <span class="badge badge-trending">
                        <i class="fas fa-star"></i> Trending
                    </span>
                    {% elif loop.index == websites|length %}
                    <span class="badge badge-new">
                        <i class="fas fa-sparkles"></i> New
                    </span>
                    {% endif %}
                    <div class="product-card-body">
                        <div class="product-logo">🛍️</div>
                        <div class="product-name">{{ website.name }}</div>
                        <span class="product-category">{{ category }}</span>
                        <div class="product-btn">
                            Visit Site <i class="fas fa-external-link-alt"></i>
                        </div>
                    </div>
                </a>
                {% endfor %}
            </div>
        </div>
        {% endfor %}

        <div class="no-results" id="noResults" style="display: none;">
            <div class="no-results-icon"><i class="fas fa-search"></i></div>
            <p class="no-results-text">No websites found matching your search</p>
            <p class="no-results-sub">Try different keywords or browse all categories</p>
        </div>
    </div>
</section>
{% endblock %}

{% block scripts %}
<script>
    const searchBox = document.getElementById('searchBox');
    const headerSearch = document.getElementById('headerSearch');
    const categoryFilter = document.getElementById('categoryFilter');
    const categorySections = document.querySelectorAll('.category-section');
    const noResults = document.getElementById('noResults');

    // Sync header search with main search
    if (headerSearch) {
        headerSearch.addEventListener('input', function() {
            searchBox.value = this.value;
            filterWebsites();
        });
    }

    function filterWebsites() {
        const searchTerm = searchBox.value.toLowerCase().trim();
        const selectedCategory = categoryFilter.value.toLowerCase();
        let hasResults = false;
        let totalVisibleCards = 0;

        categorySections.forEach(section => {
            const sectionCategory = section.dataset.category.toLowerCase();
            const cards = section.querySelectorAll('.product-card');
            let visibleCards = 0;

            const categoryMatches = selectedCategory === '' || sectionCategory === selectedCategory;

            cards.forEach(card => {
                const websiteName = card.dataset.name;
                const cardCategory = card.dataset.category.toLowerCase();

                const nameMatches = websiteName.includes(searchTerm) || searchTerm === '';
                const catMatches = selectedCategory === '' || cardCategory === selectedCategory;

                if (nameMatches && catMatches && categoryMatches) {
                    card.style.display = 'block';
                    visibleCards++;
                } else {
                    card.style.display = 'none';
                }
            });

            if (visibleCards > 0 && categoryMatches) {
                section.style.display = 'block';
                hasResults = true;
                totalVisibleCards += visibleCards;
            } else {
                section.style.display = 'none';
            }
        });

        noResults.style.display = (hasResults && totalVisibleCards > 0) ? 'none' : 'block';
    }

    searchBox.addEventListener('input', filterWebsites);
    categoryFilter.addEventListener('change', filterWebsites);

    // Animate elements on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    document.querySelectorAll('.stat-card, .product-card, .trending-card').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href !== '#') {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            }
        });
    });
</script>
{% endblock %}
'''

# ============================================================================
# LOGIN TEMPLATE
# ============================================================================
LOGIN_TEMPLATE = '''
{% extends "base" %}
{% block content %}
<div class="auth-container">
    <h1 class="auth-title">🔐 Welcome Back!</h1>

    <div class="auth-tabs">
        <button type="button" id="userTabBtn" class="auth-tab active" onclick="showLoginForm('user')">
            <i class="fas fa-user"></i> User Login
        </button>
        <button type="button" id="adminTabBtn" class="auth-tab" onclick="showLoginForm('admin')">
            <i class="fas fa-crown"></i> Admin Login
        </button>
    </div>

    <form method="POST" action="{{ url_for('login') }}" id="userLoginForm">
        <input type="hidden" name="login_type" value="user" id="loginTypeInput">
        <div class="form-group">
            <label for="username"><i class="fas fa-user"></i> Username</label>
            <input type="text" id="username" name="username" required placeholder="Enter your username">
        </div>
        <div class="form-group">
            <label for="password"><i class="fas fa-lock"></i> Password</label>
            <input type="password" id="password" name="password" required placeholder="Enter your password">
        </div>
        <button type="submit" class="btn-submit">
            <i class="fas fa-sign-in-alt"></i> Login to Account
        </button>
    </form>

    <form method="POST" action="{{ url_for('login') }}" id="adminLoginForm" style="display: none;">
        <input type="hidden" name="login_type" value="admin" id="adminLoginTypeInput">
        <div class="form-group">
            <label for="admin_username"><i class="fas fa-user-shield"></i> Admin Username</label>
            <input type="text" id="admin_username" name="username" required placeholder="Enter admin username">
        </div>
        <div class="form-group">
            <label for="admin_password"><i class="fas fa-lock"></i> Admin Password</label>
            <input type="password" id="admin_password" name="password" required placeholder="Enter admin password">
        </div>
        <button type="submit" class="btn-submit" style="background: var(--gradient-secondary);">
            <i class="fas fa-crown"></i> Login as Admin
        </button>
    </form>

    <div class="auth-switch">
        Don't have an account? <a href="{{ url_for('signup') }}">Create one here</a>
    </div>
</div>

<script>
function showLoginForm(type) {
    const userForm = document.getElementById('userLoginForm');
    const adminForm = document.getElementById('adminLoginForm');
    const userTab = document.getElementById('userTabBtn');
    const adminTab = document.getElementById('adminTabBtn');

    if (type === 'user') {
        userForm.style.display = 'block';
        adminForm.style.display = 'none';
        userTab.classList.add('active');
        adminTab.classList.remove('active');
        document.getElementById('loginTypeInput').value = 'user';
    } else {
        userForm.style.display = 'none';
        adminForm.style.display = 'block';
        userTab.classList.remove('active');
        adminTab.classList.add('active');
        document.getElementById('loginTypeInput').value = 'admin';
    }
}
</script>
{% endblock %}
'''

# ============================================================================
# SIGNUP TEMPLATE
# ============================================================================
SIGNUP_TEMPLATE = '''
{% extends "base" %}
{% block content %}
<div class="auth-container">
    <h1 class="auth-title">✨ Create Account</h1>
    <form method="POST" action="{{ url_for('signup') }}">
        <div class="form-group">
            <label for="username"><i class="fas fa-user"></i> Username</label>
            <input type="text" id="username" name="username" required placeholder="Choose a username" minlength="3">
        </div>
        <div class="form-group">
            <label for="password"><i class="fas fa-lock"></i> Password</label>
            <input type="password" id="password" name="password" required placeholder="Choose a password" minlength="6">
        </div>
        <button type="submit" class="btn-submit">
            <i class="fas fa-user-plus"></i> Create Account
        </button>
    </form>
    <div class="auth-switch">
        Already have an account? <a href="{{ url_for('login') }}">Login here</a>
    </div>
</div>
{% endblock %}
'''

# ============================================================================
# ADMIN TEMPLATE
# ============================================================================
ADMIN_TEMPLATE = '''
{% extends "base" %}
{% block content %}
<div class="container">
    <div class="admin-panel">
        <h2 class="admin-title"><i class="fas fa-tachometer-alt"></i> Admin Dashboard</h2>
        <div class="stats-bar" style="margin-bottom: 30px;">
            <div class="stat-card">
                <span class="stat-icon">🌐</span>
                <div class="stat-number">{{ total_websites }}</div>
                <div class="stat-label">Total Websites</div>
            </div>
            <div class="stat-card">
                <span class="stat-icon">👥</span>
                <div class="stat-number">{{ total_users }}</div>
                <div class="stat-label">Registered Users</div>
            </div>
            <div class="stat-card">
                <span class="stat-icon">📂</span>
                <div class="stat-number">{{ total_categories }}</div>
                <div class="stat-label">Categories</div>
            </div>
        </div>

        <!-- Dropdown Menu for Admin Sections -->
        <div class="form-group" style="margin-bottom: 25px;">
            <label for="adminSectionSelect" style="color: var(--text-secondary); font-size: 1rem; margin-bottom: 10px; display: block;">
                <i class="fas fa-list"></i> Select Admin Section:
            </label>
            <select id="adminSectionSelect" class="category-filter" style="width: 100%; min-width: auto;" onchange="showAdminSection(this.value)">
                <option value="users">👥 Users Management</option>
                <option value="websites">🌐 Website Management</option>
                <option value="remarks">💬 Reviews / Remarks</option>
            </select>
        </div>
    </div>

    <!-- Users Management Section -->
    <div class="admin-panel" id="usersSection">
        <h2 class="admin-title"><i class="fas fa-users"></i> User Management</h2>
        <table class="websites-table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Username</th>
                    <th>Status</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {% for user in users %}
                <tr>
                    <td>{{ user.id }}</td>
                    <td>{{ user.username }}</td>
                    <td>
                        {% if user.id == session.get('user_id') %}
                            <span style="color: var(--success-color); font-weight: 500;">
                                <i class="fas fa-circle" style="font-size: 8px; vertical-align: middle;"></i> Online
                            </span>
                        {% else %}
                            <span style="color: var(--text-muted);">
                                <i class="fas fa-circle" style="font-size: 8px; vertical-align: middle;"></i> Offline
                            </span>
                        {% endif %}
                    </td>
                    <td>
                        <a href="{{ url_for('admin_user_history', username=user.username) }}" class="btn-add" style="display: inline-flex; align-items: center; gap: 6px; padding: 8px 16px; font-size: 0.85rem; margin-right: 8px; background: var(--info-color);">
                            <i class="fas fa-history"></i> History
                        </a>
                        <form method="POST" action="{{ url_for('delete_user', id=user.id) }}" style="display: inline;">
                            <button type="submit" class="btn-delete" onclick="return confirm('Are you sure you want to delete user {{ user.username }}?')">
                                <i class="fas fa-trash"></i> Delete
                            </button>
                        </form>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% if not users %}
        <p style="color: var(--text-secondary); text-align: center; padding: 30px;">
            <i class="fas fa-user-slash" style="font-size: 2rem; display: block; margin-bottom: 10px;"></i>
            No registered users found.
        </p>
        {% endif %}
    </div>

    <!-- Website Management Section -->
    <div class="admin-panel" id="websitesSection" style="display: none;">
        <h2 class="admin-title"><i class="fas fa-globe"></i> Website Management</h2>

        <!-- Add Website Form -->
        <div style="margin-bottom: 25px; padding: 25px; background: var(--bg-body); border-radius: var(--radius-lg); border: 1px solid var(--border-color);">
            <h3 style="color: var(--primary-color); margin-bottom: 20px; font-size: 1.2rem;">
                <i class="fas fa-plus-circle"></i> Add New Website
            </h3>
            <form method="POST" action="{{ url_for('add_website') }}">
                <div class="admin-form">
                    <div class="form-group">
                        <label for="name">Website Name</label>
                        <input type="text" id="name" name="name" required placeholder="e.g., Amazon">
                    </div>
                    <div class="form-group">
                        <label for="category">Category</label>
                        <input type="text" id="category" name="category" required placeholder="e.g., General Shopping">
                    </div>
                    <div class="form-group">
                        <label for="link">Website Link</label>
                        <input type="url" id="link" name="link" required placeholder="https://example.com">
                    </div>
                    <button type="submit" class="btn-add">
                        <i class="fas fa-plus"></i> Add Website
                    </button>
                </div>
            </form>
        </div>

        <!-- Search by Category -->
        <div style="margin-bottom: 25px; padding: 25px; background: var(--bg-body); border-radius: var(--radius-lg); border: 1px solid var(--border-color);">
            <h3 style="color: var(--primary-color); margin-bottom: 20px; font-size: 1.2rem;">
                <i class="fas fa-filter"></i> Filter by Category
            </h3>
            <div class="search-row" style="display: flex; gap: 15px; align-items: end;">
                <div class="form-group" style="flex: 1; margin-bottom: 0;">
                    <label for="searchCategory">Select Category</label>
                    <select id="searchCategory" class="category-filter" style="width: 100%; min-width: auto;" onchange="searchByCategory(this.value)">
                        <option value="">All Categories</option>
                        {% for category in categories %}
                        <option value="{{ category }}">{{ category }}</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="form-group" style="margin-bottom: 0;">
                    <label>&nbsp;</label>
                    <button type="button" class="btn-add" style="background: var(--primary-color);" onclick="resetWebsiteSearch()">
                        <i class="fas fa-redo"></i> Reset
                    </button>
                </div>
            </div>
        </div>

        <!-- Websites Table -->
        <h3 style="color: var(--text-primary); margin-bottom: 20px; font-size: 1.2rem;">
            <i class="fas fa-list"></i> All Websites ({{ total_websites }})
        </h3>
        <table class="websites-table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Category</th>
                    <th>Link</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody id="websitesTableBody">
                {% for website in websites %}
                <tr class="website-row" data-category="{{ website.category }}">
                    <td>{{ website.id }}</td>
                    <td>{{ website.name }}</td>
                    <td>
                        <span style="background: var(--bg-badge); padding: 5px 12px; border-radius: var(--radius-full); font-size: 0.85rem;">
                            {{ website.category }}
                        </span>
                    </td>
                    <td>
                        <a href="/visit/{{ website.name | urlencode }}" target="_blank" style="color: var(--primary-color);">
                            <i class="fas fa-external-link-alt"></i> {{ website.link }}
                        </a>
                    </td>
                    <td>
                        <form method="POST" action="{{ url_for('delete_website', id=website.id) }}" style="display: inline;">
                            <button type="submit" class="btn-delete" onclick="return confirm('Are you sure you want to delete this website?')">
                                <i class="fas fa-trash"></i> Delete
                            </button>
                        </form>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>

    <!-- Remarks Management Section -->
    <div class="admin-panel" id="remarksSection" style="display: none;">
        <h2 class="admin-title"><i class="fas fa-comments"></i> User Reviews / Remarks</h2>
        
        <div class="stats-bar" style="margin-bottom: 30px;">
            <div class="stat-card">
                <span class="stat-icon">💬</span>
                <div class="stat-number">{{ total_remarks }}</div>
                <div class="stat-label">Total Remarks</div>
            </div>
        </div>

        <table class="websites-table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Message</th>
                    <th>Timestamp</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {% for remark in remarks %}
                <tr>
                    <td>{{ remark.id }}</td>
                    <td>{{ remark.name if remark.name else 'Anonymous' }}</td>
                    <td style="max-width: 400px; word-wrap: break-word;">{{ remark.message }}</td>
                    <td>{{ remark.timestamp }}</td>
                    <td>
                        <form method="POST" action="{{ url_for('delete_remark', id=remark.id) }}" style="display: inline;">
                            <button type="submit" class="btn-delete" onclick="return confirm('Are you sure you want to delete this remark?')">
                                <i class="fas fa-trash"></i> Delete
                            </button>
                        </form>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% if not remarks %}
        <p style="color: var(--text-secondary); text-align: center; padding: 30px;">
            <i class="fas fa-comment-slash" style="font-size: 2rem; display: block; margin-bottom: 10px;"></i>
            No remarks submitted yet.
        </p>
        {% endif %}
    </div>
</div>

<script>
function showAdminSection(section) {
    const usersSection = document.getElementById('usersSection');
    const websitesSection = document.getElementById('websitesSection');
    const remarksSection = document.getElementById('remarksSection');

    if (section === 'users') {
        usersSection.style.display = 'block';
        websitesSection.style.display = 'none';
        remarksSection.style.display = 'none';
    } else if (section === 'websites') {
        usersSection.style.display = 'none';
        websitesSection.style.display = 'block';
        remarksSection.style.display = 'none';
    } else if (section === 'remarks') {
        usersSection.style.display = 'none';
        websitesSection.style.display = 'none';
        remarksSection.style.display = 'block';
    }
}

function searchByCategory(category) {
    const rows = document.querySelectorAll('.website-row');
    rows.forEach(row => {
        const rowCategory = row.dataset.category;
        if (category === '' || rowCategory === category) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

function resetWebsiteSearch() {
    document.getElementById('searchCategory').value = '';
    const rows = document.querySelectorAll('.website-row');
    rows.forEach(row => {
        row.style.display = '';
    });
}
</script>
{% endblock %}
'''

# ============================================================================
# USER HISTORY TEMPLATE
# ============================================================================
USER_HISTORY_TEMPLATE = '''
{% extends "base" %}
{% block content %}
<div class="container">
    <div class="admin-panel">
        <h2 class="admin-title"><i class="fas fa-history"></i> My Browsing History</h2>
        
        <div class="stats-bar" style="margin-bottom: 30px;">
            <div class="stat-card">
                <span class="stat-icon">👁️</span>
                <div class="stat-number">{{ total_visits }}</div>
                <div class="stat-label">Total Visits</div>
            </div>
        </div>

        <table class="websites-table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Website Name</th>
                    <th>URL</th>
                    <th>Visit Time</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {% for record in history %}
                <tr>
                    <td>{{ record.id }}</td>
                    <td>{{ record.website_name }}</td>
                    <td>
                        <a href="{{ record.website_url }}" target="_blank" style="color: var(--primary-color); max-width: 400px; display: inline-block; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                            <i class="fas fa-external-link-alt"></i> {{ record.website_url }}
                        </a>
                    </td>
                    <td>{{ record.visit_time }}</td>
                    <td>
                        <a href="{{ record.website_url }}" target="_blank" class="btn-add" style="display: inline-flex; align-items: center; gap: 6px; padding: 8px 16px; font-size: 0.85rem;">
                            <i class="fas fa-external-link-alt"></i> Visit
                        </a>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% if not history %}
        <p style="color: var(--text-secondary); text-align: center; padding: 30px;">
            <i class="fas fa-history" style="font-size: 2rem; display: block; margin-bottom: 10px;"></i>
            No browsing history yet. Start visiting websites to see your history here!
        </p>
        {% endif %}
    </div>
</div>
{% endblock %}
'''

# ============================================================================
# ADMIN USER HISTORY TEMPLATE
# ============================================================================
ADMIN_USER_HISTORY_TEMPLATE = '''
{% extends "base" %}
{% block content %}
<div class="container">
    <div class="admin-panel">
        <h2 class="admin-title">
            <i class="fas fa-user-clock"></i> User History: {{ viewed_username }}
        </h2>
        
        <div style="margin-bottom: 20px;">
            <a href="{{ url_for('admin') }}" class="btn-secondary" style="display: inline-flex; align-items: center; gap: 8px; padding: 10px 20px; background: var(--bg-card); color: var(--text-primary); border: 1px solid var(--border-color); border-radius: var(--radius-md); text-decoration: none;">
                <i class="fas fa-arrow-left"></i> Back to Admin Panel
            </a>
        </div>

        <div class="stats-bar" style="margin-bottom: 30px;">
            <div class="stat-card">
                <span class="stat-icon">👁️</span>
                <div class="stat-number">{{ total_visits }}</div>
                <div class="stat-label">Total Visits</div>
            </div>
        </div>

        <table class="websites-table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Website Name</th>
                    <th>URL</th>
                    <th>Visit Time</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {% for record in history %}
                <tr>
                    <td>{{ record.id }}</td>
                    <td>{{ record.website_name }}</td>
                    <td>
                        <a href="{{ record.website_url }}" target="_blank" style="color: var(--primary-color); max-width: 400px; display: inline-block; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                            <i class="fas fa-external-link-alt"></i> {{ record.website_url }}
                        </a>
                    </td>
                    <td>{{ record.visit_time }}</td>
                    <td>
                        <a href="{{ record.website_url }}" target="_blank" class="btn-add" style="display: inline-flex; align-items: center; gap: 6px; padding: 8px 16px; font-size: 0.85rem;">
                            <i class="fas fa-external-link-alt"></i> Visit
                        </a>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% if not history %}
        <p style="color: var(--text-secondary); text-align: center; padding: 30px;">
            <i class="fas fa-user-slash" style="font-size: 2rem; display: block; margin-bottom: 10px;"></i>
            No browsing history found for this user.
        </p>
        {% endif %}
    </div>
</div>
{% endblock %}
'''


@app.route('/')
def index():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM websites ORDER BY category, name')
    websites = cursor.fetchall()

    cursor.execute('SELECT COUNT(*) FROM websites')
    total_websites = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(DISTINCT category) FROM websites')
    total_categories = cursor.fetchone()[0]

    cursor.execute('SELECT DISTINCT category FROM websites ORDER BY category')
    categories = [row[0] for row in cursor.fetchall()]

    conn.close()

    websites_by_category = {}
    for website in websites:
        if website['category'] not in websites_by_category:
            websites_by_category[website['category']] = []
        websites_by_category[website['category']].append(website)

    return render_template_string(
        BASE_TEMPLATE.replace('{% block content %}{% endblock %}', INDEX_TEMPLATE.replace('{% extends "base" %}', '').replace('{% block content %}', '').replace('{% endblock %}', '').replace('{% block scripts %}', '<!-- scripts -->').replace('{% endblock %}', '')),
        title='Home',
        websites_by_category=websites_by_category,
        total_websites=total_websites,
        total_categories=total_categories,
        categories=categories
    )


@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('user_id'):
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        login_type = request.form.get('login_type', 'user')

        # Admin credentials check
        ADMIN_USERNAME = 'kaml@admin'
        ADMIN_PASSWORD = 'kamlesh@123'

        if login_type == 'admin' or username == ADMIN_USERNAME:
            # Admin login
            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                session['user_id'] = 'admin'
                session['username'] = username
                session['is_admin'] = True
                flash('Admin login successful! Welcome to Admin Panel.', 'success')
                return redirect(url_for('admin'))
            else:
                flash('Invalid admin credentials.', 'error')
        else:
            # Regular user login
            hashed_password = hashlib.sha256(password.encode()).hexdigest()

            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, hashed_password))
            user = cursor.fetchone()
            conn.close()

            if user:
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['is_admin'] = False
                flash('Login successful! Welcome back.', 'success')
                return redirect(url_for('index'))
            else:
                flash('Invalid username or password.', 'error')

    return render_template_string(
        BASE_TEMPLATE.replace('{% block content %}{% endblock %}', LOGIN_TEMPLATE.replace('{% extends "base" %}', '').replace('{% block content %}', '').replace('{% endblock %}', '')),
        title='Login'
    )


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if session.get('user_id'):
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        if len(username) < 3:
            flash('Username must be at least 3 characters long.', 'error')
            return render_template_string(
                BASE_TEMPLATE.replace('{% block content %}{% endblock %}', SIGNUP_TEMPLATE.replace('{% extends "base" %}', '').replace('{% block content %}', '').replace('{% endblock %}', '')),
                title='Sign Up'
            )

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return render_template_string(
                BASE_TEMPLATE.replace('{% block content %}{% endblock %}', SIGNUP_TEMPLATE.replace('{% extends "base" %}', '').replace('{% block content %}', '').replace('{% endblock %}', '')),
                title='Sign Up'
            )

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
            conn.commit()
            conn.close()

            flash('Account created successfully! Please login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists. Please choose another.', 'error')

    return render_template_string(
        BASE_TEMPLATE.replace('{% block content %}{% endblock %}', SIGNUP_TEMPLATE.replace('{% extends "base" %}', '').replace('{% block content %}', '').replace('{% endblock %}', '')),
        title='Sign Up'
    )


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('index'))


@app.route('/admin')
@admin_required
def admin():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM websites ORDER BY category, name')
    websites = cursor.fetchall()

    cursor.execute('SELECT COUNT(*) FROM websites')
    total_websites = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(DISTINCT category) FROM websites')
    total_categories = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM users')
    total_users = cursor.fetchone()[0]

    cursor.execute('SELECT * FROM users ORDER BY id')
    users = cursor.fetchall()

    cursor.execute('SELECT DISTINCT category FROM websites ORDER BY category')
    categories = [row[0] for row in cursor.fetchall()]

    cursor.execute('SELECT * FROM remarks ORDER BY timestamp DESC')
    remarks = cursor.fetchall()

    cursor.execute('SELECT COUNT(*) FROM remarks')
    total_remarks = cursor.fetchone()[0]

    conn.close()

    return render_template_string(
        BASE_TEMPLATE.replace('{% block content %}{% endblock %}', ADMIN_TEMPLATE.replace('{% extends "base" %}', '').replace('{% block content %}', '').replace('{% endblock %}', '')),
        title='Admin Panel',
        websites=websites,
        total_websites=total_websites,
        total_categories=total_categories,
        total_users=total_users,
        users=users,
        categories=categories,
        remarks=remarks,
        total_remarks=total_remarks
    )


@app.route('/add', methods=['POST'])
@admin_required
def add_website():
    name = request.form['name'].strip()
    category = request.form['category'].strip()
    link = request.form['link'].strip()

    if name and category and link:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO websites (name, category, link) VALUES (?, ?, ?)', (name, category, link))
        conn.commit()
        conn.close()
        flash(f'Website "{name}" added successfully!', 'success')
    else:
        flash('All fields are required.', 'error')

    return redirect(url_for('admin'))


@app.route('/delete/<int:id>', methods=['POST'])
@admin_required
def delete_website(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM websites WHERE id = ?', (id,))
    website = cursor.fetchone()

    if website:
        cursor.execute('DELETE FROM websites WHERE id = ?', (id,))
        conn.commit()
        flash(f'Website "{website["name"]}" deleted successfully!', 'success')
    else:
        flash('Website not found.', 'error')

    conn.close()
    return redirect(url_for('admin'))


@app.route('/delete_user/<int:id>', methods=['POST'])
@admin_required
def delete_user(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT username FROM users WHERE id = ?', (id,))
    user = cursor.fetchone()

    if user:
        cursor.execute('DELETE FROM users WHERE id = ?', (id,))
        conn.commit()
        flash(f'User "{user["username"]}" deleted successfully!', 'success')
    else:
        flash('User not found.', 'error')

    conn.close()
    return redirect(url_for('admin'))


# ============================================================================
# REMARKS/FEEDBACK ROUTES
# ============================================================================

@app.route('/submit_remark', methods=['POST'])
def submit_remark():
    name = request.form.get('name', '').strip()
    message = request.form.get('message', '').strip()

    if message:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO remarks (name, message) VALUES (?, ?)', (name, message))
        conn.commit()
        conn.close()
        flash('Thank you for your feedback!', 'success')
    else:
        flash('Message is required.', 'error')

    # Redirect back to the referring page or home
    return redirect(request.referrer or url_for('index'))


@app.route('/admin/delete_remark/<int:id>', methods=['POST'])
@admin_required
def delete_remark(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT name, message FROM remarks WHERE id = ?', (id,))
    remark = cursor.fetchone()

    if remark:
        cursor.execute('DELETE FROM remarks WHERE id = ?', (id,))
        conn.commit()
        remark_name = remark['name'] if remark['name'] else 'Anonymous'
        flash(f'Remark from "{remark_name}" deleted successfully!', 'success')
    else:
        flash('Remark not found.', 'error')

    conn.close()
    return redirect(url_for('admin'))


# ============================================================================
# USER HISTORY TRACKING ROUTES
# ============================================================================

@app.route('/visit/<path:site_name>')
def visit_website(site_name):
    """Track user visits to websites and redirect to actual URL"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get the website from database by name
    cursor.execute('SELECT name, link FROM websites WHERE name = ?', (site_name,))
    website = cursor.fetchone()
    
    if website:
        # Track the visit if user is logged in
        if session.get('user_id'):
            username = session.get('username', 'Anonymous')
            cursor.execute(
                'INSERT INTO user_history (username, website_name, website_url) VALUES (?, ?, ?)',
                (username, website['name'], website['link'])
            )
            conn.commit()
        
        conn.close()
        
        # Redirect to the actual website
        if website['link'].startswith('http'):
            return redirect(website['link'])
        else:
            return redirect('https://' + website['link'])
    else:
        conn.close()
        flash('Website not found.', 'error')
        return redirect(url_for('index'))


@app.route('/user/history')
@login_required
def user_history():
    """Show logged-in user's own history"""
    username = session.get('username')
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute(
        'SELECT * FROM user_history WHERE username = ? ORDER BY visit_time DESC',
        (username,)
    )
    history = cursor.fetchall()
    
    cursor.execute('SELECT COUNT(*) FROM user_history WHERE username = ?', (username,))
    total_visits = cursor.fetchone()[0]
    
    conn.close()
    
    return render_template_string(
        BASE_TEMPLATE.replace('{% block content %}{% endblock %}', USER_HISTORY_TEMPLATE.replace('{% extends "base" %}', '').replace('{% block content %}', '').replace('{% endblock %}', '')),
        title='My History',
        history=history,
        total_visits=total_visits
    )


@app.route('/admin/user_history/<username>')
@admin_required
def admin_user_history(username):
    """Admin view: Show specific user's history"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute(
        'SELECT * FROM user_history WHERE username = ? ORDER BY visit_time DESC',
        (username,)
    )
    history = cursor.fetchall()
    
    cursor.execute('SELECT COUNT(*) FROM user_history WHERE username = ?', (username,))
    total_visits = cursor.fetchone()[0]
    
    conn.close()
    
    return render_template_string(
        BASE_TEMPLATE.replace('{% block content %}{% endblock %}', ADMIN_USER_HISTORY_TEMPLATE.replace('{% extends "base" %}', '').replace('{% block content %}', '').replace('{% endblock %}', '')),
        title=f'History - {username}',
        history=history,
        total_visits=total_visits,
        viewed_username=username
    )


if __name__ == '__main__':
    init_db()
    print("=" * 50)
    print("🚀 App Linker is starting...")
    print("=" * 50)
    print("📌 Admin Credentials:")
    print("   Username: kaml@admin")
    print("   Password: kamlesh@123")
    print("=" * 50)
    print("🌐 Open http://localhost:5000 in your browser")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)
