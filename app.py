import datetime as dt
import json

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

import auth
from database import (create_user, get_db, get_profile, get_state, get_user_by_name,
                      init_db, save_profile, save_state)

app = FastAPI(title="Baby Prep Dashboard")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

init_db()

# size_targets = how many pieces baby needs IN ROTATION while in that size
# (EU sizes are the baby's max height in cm; 50 ≈ birth–6 weeks, 56 ≈ 1–3
# months, 62 ≈ 3–6 months). Defaults follow the usual guidance: keep size 50
# small because the stage is short, carry the working wardrobe in 56/62.
WARDROBE = [
    {"id":"body","name":"Long-sleeve bodysuit","type":"Base","icon":"▱","brand":"Sanetta","sizes":["50","56","62"],"size_targets":{"50":4,"56":6,"62":6},"unit":"pieces","note":"Your everyday base layer. Keep several in easy-wash cotton.","preferred_colors":["white","beige","soft peachy pink"]},
    {"id":"sleep","name":"Footed sleepsuit / all-in-one","type":"Sleep","icon":"☾","brand":"Sanetta","sizes":["50","56","62"],"size_targets":{"50":3,"56":5,"62":5},"unit":"pieces","note":"Useful for nights and simple daytime outfits. Footed versions reduce the need for socks."},
    {"id":"romper","name":"Romper","type":"Day","icon":"✿","brand":"Little Dutch","sizes":["50","56","62"],"size_targets":{"50":1,"56":3,"62":3},"unit":"pieces","note":"A cute one-piece daytime option; add socks/booties if legs are uncovered."},
    {"id":"trousers","name":"Trousers / leggings","type":"Day","icon":"✿","brand":"Mayoral","sizes":["50","56","62"],"size_targets":{"50":1,"56":3,"62":3},"unit":"pieces","note":"Pair with a long-sleeve bodysuit."},
    {"id":"cardigan","name":"Soft cardigan","type":"Layer","icon":"⌁","brand":"Little Dutch / Mayoral","sizes":["56","62"],"size_targets":{"56":2,"62":2},"unit":"pieces","note":"Prefer several light layers over one very heavy layer."},
    {"id":"top","name":"Long-sleeve top","type":"Day","icon":"✿","brand":"Mayoral / Next","sizes":["56","62"],"size_targets":{"56":2,"62":2},"unit":"pieces","note":"Use over a bodysuit when you want a more dressed look."},
    {"id":"knitromper","name":"Sleeveless knitted romper / pinafore","type":"Cute","icon":"♡","brand":"Little Dutch","sizes":["56","62"],"size_targets":{"56":2,"62":2},"unit":"pieces","note":"Layer over a long-sleeve bodysuit or top."},
    {"id":"socks","name":"Socks / booties","type":"Accessory","icon":"◌","brand":"Sanetta","sizes":["50","56","62"],"size_targets":{"50":3,"56":6,"62":6},"unit":"pairs","note":"Only needed when feet are not covered by the outfit."},
    {"id":"hat","name":"Warm hat","type":"Outdoor","icon":"❄","brand":"Sanetta / Next","sizes":["50","56","62"],"size_targets":{"50":1,"56":2,"62":1},"unit":"pieces","note":"For outdoor cold. Remove indoors and in warm cars/public transport."},
    {"id":"outer","name":"Warm outer suit / pramsuit","type":"Outdoor","icon":"❄","brand":"","sizes":["50","56","62"],"size_targets":{"50":1,"56":1,"62":1},"unit":"piece","note":"For outdoor winter use. The exact outer layer depends on temperature and transport setup."},
]

# Sleep is its own top-level category, filtered by group like clothing is
# filtered by type. Sleepwear ids stay stable so saved quantities in
# localStorage keep working.
SLEEP = [
    {"id":"swaddle","name":"Swaddle","type":"Essential","icon":"☾","brand":"MomCozy","sizes":["50–62"],"target":2,"unit":"pieces","note":"Light breathable swaddle or sleepsack for safe sleep.","purchase_url":"https://de.momcozy.com/products/breathable-newborn-swaddle-for-cooler-comfier-sleep-copy-1?variant=49916095267056","group":"Essentials"},
    {"id":"sleevesack","name":"Sleeveless sleepsack","type":"Essential","icon":"☾","brand":"","sizes":["50–62"],"target":1,"unit":"piece","note":"Sleeveless sleepsack for safe, layered sleep. Consider one to alternate with swaddles.","group":"Essentials"},
    {"id":"crib","name":"Crib","type":"Essential","icon":"🛏️","brand":"","target":1,"unit":"piece","note":"The main safe sleep space; a full-size crib lasts into toddlerhood.","group":"Essentials"},
    {"id":"bassinet","name":"Bassinet or bedside sleeper","type":"Essential","icon":"🛌","brand":"","target":1,"unit":"piece","note":"Keeps baby within arm's reach for night feeds in the first months.","group":"Essentials"},
    {"id":"cribmattress","name":"Crib mattress","type":"Essential","icon":"📏","brand":"","target":1,"unit":"piece","note":"Firm, flat and snug-fitting, with no gap to the crib frame.","group":"Essentials"},
    {"id":"cribsheets","name":"Crib sheets","type":"Essential","icon":"🧺","brand":"","target":2,"unit":"pieces","note":"Keep a spare so a wet sheet never leaves the crib uncovered.","group":"Essentials"},
    {"id":"monitor","name":"Baby monitor","type":"Optional","icon":"📡","brand":"","target":1,"unit":"piece","note":"Peace of mind once baby sleeps in a separate room.","group":"Optional"},
    {"id":"whitenoise","name":"White noise machine","type":"Optional","icon":"🔊","brand":"","target":1,"unit":"piece","note":"Helps some babies settle; keep the volume low and place it away from the crib.","group":"Optional"},
]

# Awake-time and play items.
LEISURE = [
    {"id":"playgym","name":"Activity gym / mat","type":"Leisure","icon":"🤸","brand":"","target":1,"unit":"piece","note":"For tummy time and early reaching; swapping the arch toys keeps it interesting."},
    {"id":"books","name":"Books","type":"Leisure","icon":"📖","brand":"","target":3,"unit":"pieces","note":"Cloth and board books — reading aloud starts on day one; high-contrast pages suit newborn eyes."},
    {"id":"plush","name":"Soft plush toys","type":"Leisure","icon":"🧸","brand":"","target":2,"unit":"pieces","note":"Cuddly comfort. Keep plush out of the crib for sleep in the first months."},
    {"id":"toys","name":"Toys","type":"Leisure","icon":"🪀","brand":"","target":3,"unit":"pieces","note":"A few high-contrast rattles and grasping toys; rotating a small set beats a pile."},
]

# Diapering, bath and care gear, grouped like the sleep section
# (targets are editable planning defaults; "packs" items assume you restock).
CARE = [
    {"id":"changepad","name":"Changing pad","type":"Diapering","icon":"🧷","brand":"","target":1,"unit":"piece","note":"A washable mat for changes at home and on the go.","group":"Diapering"},
    {"id":"padcovers","name":"Changing pad covers","type":"Diapering","icon":"🧺","brand":"","target":2,"unit":"pieces","note":"Keep a spare so a wet cover never stops a change.","group":"Diapering"},
    {"id":"changingtable","name":"Changing table","type":"Diapering","icon":"🪑","brand":"","target":1,"unit":"piece","note":"A comfortable-height changing spot; always keep one hand on the baby.","group":"Diapering"},
    {"id":"cream","name":"Cream / ointment","type":"Diapering","icon":"🧴","brand":"","target":1,"unit":"piece","note":"Barrier cream for sore bottoms; a little goes a long way.","group":"Diapering"},
    {"id":"diapers","name":"Diapers","type":"Diapering","icon":"🧻","brand":"","target":2,"unit":"packs","note":"Newborns use 8–10 diapers a day. Start with two newborn-size packs and buy more once the fit is confirmed.","group":"Diapering"},
    {"id":"diaperbag","name":"Diaper bag","type":"Diapering","icon":"🎒","brand":"","target":1,"unit":"piece","note":"One bag that stays packed: diapers, wipes, change of clothes, pad.","group":"Diapering"},
    {"id":"wipes","name":"Wipes","type":"Diapering","icon":"💧","brand":"","target":2,"unit":"packs","note":"Fragrance-free for newborn skin; one pack for the table, one for the bag.","group":"Diapering"},

    {"id":"bathtub","name":"Bathtub","type":"Bath","icon":"🛁","brand":"","target":1,"unit":"piece","note":"A small baby tub or sink insert for the first months.","group":"Bath"},
    {"id":"towels","name":"Towels","type":"Bath","icon":"🧣","brand":"","target":3,"unit":"pieces","note":"Hooded cotton towels; one in use, one in the wash, one spare.","group":"Bath"},
    {"id":"washcloths","name":"Washcloths","type":"Bath","icon":"🫧","brand":"","target":4,"unit":"pieces","note":"Soft cloths for face and body; handy at the changing table too.","group":"Bath"},
    {"id":"bathsupport","name":"Baby bath support","type":"Bath","icon":"🧽","brand":"","target":1,"unit":"piece","note":"Keeps baby safely reclined during the bath.","group":"Bath"},
    {"id":"baththermometer","name":"Bath thermometer","type":"Bath","icon":"🌡️","brand":"","target":1,"unit":"piece","note":"Aim for around 37–38°C; the elbow test works too.","group":"Bath"},
    {"id":"shampoo","name":"Mild shampoo / body wash","type":"Bath","icon":"🧼","brand":"","target":1,"unit":"piece","note":"pH-neutral baby wash; newborns need only a little.","group":"Bath"},

    {"id":"babythermometer","name":"Baby thermometer","type":"Care","icon":"🤒","brand":"","target":1,"unit":"piece","note":"A fast digital thermometer for fever checks.","group":"Care"},
    {"id":"firstaid","name":"First aid kit","type":"Care","icon":"🩹","brand":"","target":1,"unit":"piece","note":"Basics for small emergencies; keep the pediatrician's number with it.","group":"Care"},
    {"id":"nasalaspirator","name":"Nasal aspirator","type":"Care","icon":"👃","brand":"","target":1,"unit":"piece","note":"Clears a blocked nose before feeds and sleep.","group":"Care"},
    {"id":"pacifiers","name":"Pacifiers","type":"Care","icon":"😙","brand":"","target":2,"unit":"pieces","note":"Babies are picky about shapes; try one or two and keep a spare.","group":"Care"},
    {"id":"teethers","name":"Teethers","type":"Care","icon":"🦷","brand":"","target":2,"unit":"pieces","note":"Chillable teethers for gum comfort; useful from a few months.","group":"Care"},
    {"id":"brushcomb","name":"Brush & comb","type":"Care","icon":"💈","brand":"","target":1,"unit":"piece","note":"Soft-bristle brush for the first hair and cradle-cap care.","group":"Care"},
]

# Big-ticket gear for transport and safe places to put baby down.
GEAR = [
    {"id":"stroller","name":"Stroller","type":"Gear","icon":"🚼","brand":"","target":1,"unit":"piece","note":"The daily workhorse. Check it fits your car boot and hallway; a lie-flat or bassinet option is best for newborns."},
    {"id":"carseat","name":"Infant car seat","type":"Gear","icon":"💺","brand":"","target":1,"unit":"piece","note":"Needed from the first ride home. i-Size (R129) is the current EU standard; a stay-in car base makes loading easier."},
    {"id":"carrier","name":"Structured carrier or wrap carrier","type":"Gear","icon":"🎒","brand":"","target":1,"unit":"piece","note":"Hands-free closeness; newborn-friendly wraps or carriers with infant inserts work from day one."},
    {"id":"bouncer","name":"Bouncer","type":"Gear","icon":"🪑","brand":"","target":1,"unit":"piece","note":"A safe spot to put baby down awake; the gentle bounce soothes many newborns."},
    {"id":"playard","name":"Playard / travel crib","type":"Gear","icon":"🧳","brand":"","target":1,"unit":"piece","note":"A portable sleep and play spot for travel and grandparents' houses."},
    {"id":"swing","name":"Swing","type":"Gear","icon":"🛝","brand":"","target":1,"unit":"piece","note":"Powered soothing for fussy phases; a nice-to-have — try one before buying if you can."},
]

OUTFITS = [
    {"name":"Everyday soft","emoji":"☁️","layers":["Long-sleeve bodysuit","Romper","Socks / booties"],"when":"Home / daytime"},
    {"name":"Pretty + practical","emoji":"🌸","layers":["Long-sleeve bodysuit","Trousers / leggings","Soft cardigan","Socks / booties"],"when":"Daytime / visitors"},
    {"name":"Knitted little outfit","emoji":"🧶","layers":["Long-sleeve bodysuit","Long-sleeve top","Sleeveless knitted romper / pinafore","Socks / booties"],"when":"Daytime / photos"},
    {"name":"Night","emoji":"🌙","layers":["Long-sleeve bodysuit","Footed sleepsuit / all-in-one","Swaddle or sleepsack"],"when":"Sleep"},
    {"name":"Winter outside","emoji":"❄️","layers":["Day outfit","Warm outer suit / pramsuit","Warm hat"],"when":"Outside"},
]

# Brand pools for the shopping strategy: curated starting points the user
# picks from and can extend with their own brands (saved in the browser).
BRAND_TIERS = [
    {"id":"quality","name":"High-quality basics","note":"Bodies, sleepsuits, socks and other repeat-wash basics that touch skin all day.","brands":["Sanetta","Steiff","Schlösser","Maximo","Cosilana","Engel","Disana","Hugo Boss Baby"]},
    {"id":"value","name":"Cute outfits for a good price","note":"Prettier rompers, knit layers, trousers and going-out combinations.","brands":["Little Dutch","Mayoral","Next","H&M","C&A","Zara","Name it"]},
]

# Brand suggestion pools per category. Clothing cards use the two strategy
# tiers above; these pools serve the non-clothing sections. Typing a new brand
# on a card adds it to that category's suggestions automatically.
CATEGORY_BRANDS = {
    "sleep": ["MomCozy", "Ergobaby", "Love to Dream", "aden + anais", "roba", "Fillikid", "Kinderkraft", "IKEA"],
    "care": ["Pampers", "Huggies", "WaterWipes", "Sudocrem", "Bepanthen", "Weleda", "Penaten", "Mustela", "Frida Baby", "NUK", "MAM", "Philips Avent", "Chicco"],
    "gear": ["Bugaboo", "Cybex", "Maxi-Cosi", "BabyBjörn", "Ergobaby", "Thule", "Babyzen", "Joolz", "Stokke", "Nuna", "Joie"],
    "leisure": ["Fisher-Price", "Tiny Love", "VTech", "Lamaze", "HABA", "Jellycat", "sigikid", "Steiff", "Usborne"],
    "mom": ["Medela", "Ardo", "Lansinoh", "Philips Avent", "Elvie", "Haakaa", "Silverette", "Anita", "Triumph", "Freya", "Always"],
}

# Mum's own kit: nursing essentials and postpartum care.
MOM = [
    {"id":"nursingpads","name":"Nursing pads","type":"Nursing","icon":"☁️","brand":"","target":2,"unit":"packs","note":"Leak protection between feeds; disposables for the first weeks, washable for later.","group":"Nursing"},
    {"id":"silvercups","name":"Silver cups","type":"Nursing","icon":"🥈","brand":"","target":1,"unit":"pair","note":"Silver nursing cups protect and soothe sore nipples between feeds — no cream needed while wearing them.","group":"Nursing"},
    {"id":"milkpumps","name":"Milk pumps","type":"Nursing","icon":"🍼","brand":"","target":1,"unit":"piece","note":"Electric for regular pumping, small manual for occasional. German statutory insurance usually covers one with a prescription.","group":"Nursing"},
    {"id":"nursingbras","name":"Nursing bras","type":"Nursing","icon":"🎀","brand":"","target":3,"unit":"pieces","note":"Buy from ~week 34 when size has settled; stretchy, front-opening, one in the wash at all times.","group":"Nursing"},
    {"id":"nursingpillow","name":"Nursing pillow","type":"Nursing","icon":"🤱","brand":"","target":1,"unit":"piece","note":"Supports feeding positions — and doubles as a tummy-time support later.","group":"Nursing"},
    {"id":"nipplecream","name":"Nipple creams","type":"Nursing","icon":"🧴","brand":"","target":1,"unit":"piece","note":"Pure lanolin is safe for baby; a little goes a long way.","group":"Nursing"},

    {"id":"maternitypads","name":"Maternity pads","type":"Health & care","icon":"🩸","brand":"","target":3,"unit":"packs","note":"The thick kind for the first days and weeks postpartum.","group":"Health & care"},
    {"id":"maternityunderwear","name":"Maternity underwear","type":"Health & care","icon":"🩲","brand":"","target":4,"unit":"pieces","note":"High-waisted, soft-waist briefs that hold pads securely and sit comfortably.","group":"Health & care"},
    {"id":"pyjamas","name":"Comfortable pyjamas","type":"Health & care","icon":"😴","brand":"","target":2,"unit":"pieces","note":"Button-front tops make nursing easier; darker or patterned fabrics hide leaks.","group":"Health & care"},
]

SEASONS = {12: "Winter", 1: "Winter", 2: "Winter", 3: "Spring", 4: "Spring", 5: "Spring",
           6: "Summer", 7: "Summer", 8: "Summer", 9: "Autumn", 10: "Autumn", 11: "Autumn"}
SEASON_EMOJI = {"Winter": "❄️", "Spring": "🌸", "Summer": "☀️", "Autumn": "🍂"}


# Community-ready tips shown in their own section, grouped by topic.
TIPS = [
    {"title": "One extra layer", "group": "Clothing", "icon": "🧣",
     "text": "A practical winter starting point is one more layer than an adult would wear. Adjust for the room, the weather, and your baby's temperature rather than dressing by a fixed outfit formula.",
     "source": "NHS guidance"},
    {"title": "Zips beat buttons", "group": "Clothing", "icon": "🧥",
     "text": "When buying rompers and bodysuits, prefer styles with a zip (or a double zip) rather than buttons. If zip styles aren't available, choose front or crotch snaps — and avoid pull-over-the-head designs to make dressing and nappy changes easier.",
     "source": None},
    {"title": "Light layers over one heavy one", "group": "Clothing", "icon": "🧶",
     "text": "Several thin layers trap warmth better than one thick layer, and they're far easier to fine-tune indoors, in the car, or outside.",
     "source": None},
    {"title": "Keep sleep separate from cute layering", "group": "Sleep", "icon": "🌙",
     "text": "For sleep, think sleepsuit plus an appropriate sleep bag rather than cardigans, bulky jumpers, or loose extra layers. Check the sleep-bag manufacturer's TOG guidance against the room temperature, and remove hats indoors.",
     "source": "NHS guidance"},
]

# Classic pregnancy size comparisons, gestational week -> (thing, emoji).
BABY_SIZES = {
    8: ("raspberry", "🫐"), 9: ("green olive", "🫒"), 10: ("kumquat", "🍊"),
    11: ("lime", "🍋"), 12: ("plum", "🍑"), 13: ("peach", "🍑"),
    14: ("lemon", "🍋"), 15: ("apple", "🍎"), 16: ("avocado", "🥑"),
    17: ("pear", "🍐"), 18: ("bell pepper", "🫑"), 19: ("tomato", "🍅"),
    20: ("banana", "🍌"), 21: ("carrot", "🥕"), 22: ("papaya", "🥭"),
    23: ("grapefruit", "🍊"), 24: ("ear of corn", "🌽"), 25: ("rutabaga", "🥔"),
    26: ("zucchini", "🥒"), 27: ("cauliflower", "🥦"), 28: ("eggplant", "🍆"),
    29: ("butternut squash", "🎃"), 30: ("cabbage", "🥬"), 31: ("coconut", "🥥"),
    32: ("jicama", "🥔"), 33: ("pineapple", "🍍"), 34: ("cantaloupe", "🍈"),
    35: ("honeydew melon", "🍈"), 36: ("romaine lettuce", "🥬"),
    37: ("bunch of Swiss chard", "🥬"), 38: ("leek", "🥬"),
    39: ("mini watermelon", "🍉"), 40: ("small pumpkin", "🎃"),
    41: ("watermelon", "🍉"), 42: ("watermelon", "🍉"),
}


def baby_now(due_date_str: str, baby_name):
    """Cute 'how big is the baby now' card data from the due date."""
    try:
        due = dt.date.fromisoformat(due_date_str)
    except (TypeError, ValueError):
        return None
    today = dt.date.today()
    days_left = (due - today).days
    if days_left < 0:
        return {
            "emoji": "👶", "title": "Welcome to the world!",
            "text": f"{'Baby' if not baby_name else baby_name} has arrived — the prep is done, enjoy it.",
            "footer": "🎉 so happy for you 🎉",
        }
    week = max(8, min(42, 40 - days_left // 7))
    size_name, size_emoji = BABY_SIZES[max(w for w in BABY_SIZES if w <= week)]
    if days_left > 84:
        flower, stage = "🌱", "sprouting"
    elif days_left > 28:
        flower, stage = "🌿", "growing"
    else:
        flower, stage = "🌸", "blooming"
    display = baby_name or "your little one"
    return {
        "emoji": size_emoji,
        "title": f"About the size of a {size_name}",
        "text": f"Week {week} — {display} is {stage} {flower}",
        "footer": f"{flower} {days_left} days to go {flower}",
    }


def view_context(user) -> dict:
    """Profile plus everything derived from it for the dashboard template."""
    with get_db() as db:
        profile = get_profile(db, user["id"])
    season_label, days_to_due, arrived = "Winter", None, False
    if profile["due_date"]:
        try:
            due = dt.date.fromisoformat(profile["due_date"])
            season_label = SEASONS.get(due.month, "Winter")
            days_to_due = (due - dt.date.today()).days
            if days_to_due < 0:
                arrived, days_to_due = True, None
        except ValueError:
            pass
    return {
        **profile,
        "season_label": season_label,
        "season_emoji": SEASON_EMOJI.get(season_label, "❄️"),
        "arrived": arrived,
        "days_to_due": days_to_due,
        "baby_display": profile["baby_name"] or "your little one",
        "username": user["username"],
        "baby_now": baby_now(profile["due_date"], profile["baby_name"]),
    }


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    user = auth.current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=303)
    with get_db() as db:
        state = get_state(db, user["id"])
    return templates.TemplateResponse(request, "index.html", {
        **view_context(user),
        "server_theme": state.get("theme"),
        "wardrobe": WARDROBE,
        "sleep": SLEEP,
        "care": CARE,
        "gear": GEAR,
        "leisure": LEISURE,
        "mom": MOM,
        "tips": TIPS,
        "brand_tiers": BRAND_TIERS,
        "category_brands": CATEGORY_BRANDS,
        "outfits": OUTFITS,
    })


MAX_STATE_BYTES = 100_000


@app.get("/api/state")
async def read_state(request: Request):
    user = auth.current_user(request)
    if not user:
        return JSONResponse({"error": "not logged in"}, status_code=401)
    with get_db() as db:
        return JSONResponse(get_state(db, user["id"]))


@app.post("/api/state")
async def write_state(request: Request):
    user = auth.current_user(request)
    if not user:
        return JSONResponse({"error": "not logged in"}, status_code=401)
    raw = await request.body()
    if len(raw) > MAX_STATE_BYTES:
        return JSONResponse({"error": "state too large"}, status_code=400)
    try:
        state = json.loads(raw)
    except ValueError:
        return JSONResponse({"error": "invalid json"}, status_code=400)
    if not isinstance(state, dict):
        return JSONResponse({"error": "invalid state"}, status_code=400)
    with get_db() as db:
        save_state(db, user["id"], state)
    return JSONResponse({"ok": True})


@app.post("/api/theme")
async def set_theme(request: Request):
    user = auth.current_user(request)
    if not user:
        return JSONResponse({"error": "not logged in"}, status_code=401)
    try:
        body = json.loads(await request.body())
        theme = body.get("theme")
    except ValueError:
        theme = None
    if theme not in ("peach", "ocean", "burgundy", "prune"):
        return JSONResponse({"error": "unknown theme"}, status_code=400)
    with get_db() as db:
        state = get_state(db, user["id"])
        state["theme"] = theme
        save_state(db, user["id"], state)
    return JSONResponse({"ok": True})


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: str = ""):
    if auth.current_user(request):
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse(request, "login.html", {"error": error})


@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    with get_db() as db:
        user = auth.authenticate(db, username, password)
        if not user:
            return templates.TemplateResponse(
                request, "login.html",
                {"error": "Wrong username or password."}, status_code=401)
        token = auth.create_session(db, user["id"])
    response = RedirectResponse("/", status_code=303)
    response.set_cookie(auth.SESSION_COOKIE, token, httponly=True, samesite="lax")
    return response


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request, error: str = ""):
    if auth.current_user(request):
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse(request, "register.html", {"error": error})


@app.post("/register")
async def register(request: Request, username: str = Form(...),
                   password: str = Form(...), password2: str = Form(...)):
    username = username.strip()
    if len(username) < 3:
        return templates.TemplateResponse(request, "register.html",
            {"error": "Username needs at least 3 characters."}, status_code=400)
    if len(password) < 6:
        return templates.TemplateResponse(request, "register.html",
            {"error": "Password needs at least 6 characters."}, status_code=400)
    if password != password2:
        return templates.TemplateResponse(request, "register.html",
            {"error": "The two passwords don't match."}, status_code=400)
    with get_db() as db:
        if get_user_by_name(db, username):
            return templates.TemplateResponse(request, "register.html",
                {"error": "That username is already taken."}, status_code=400)
        user_id = create_user(db, username, auth.hash_password(password))
        token = auth.create_session(db, user_id)
    response = RedirectResponse("/settings?welcome=1", status_code=303)
    response.set_cookie(auth.SESSION_COOKIE, token, httponly=True, samesite="lax")
    return response


@app.post("/logout")
async def logout(request: Request):
    token = request.cookies.get(auth.SESSION_COOKIE)
    if token:
        with get_db() as db:
            auth.destroy_session(db, token)
    response = RedirectResponse("/login", status_code=303)
    response.delete_cookie(auth.SESSION_COOKIE)
    return response


@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request, welcome: str = "", error: str = ""):
    user = auth.current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=303)
    with get_db() as db:
        profile = get_profile(db, user["id"])
        theme = get_state(db, user["id"]).get("theme") or "peach"
    return templates.TemplateResponse(request, "settings.html", {
        **profile, "username": user["username"], "welcome": welcome,
        "error": error, "theme": theme})


@app.post("/settings")
async def settings_save(request: Request, baby_name: str = Form(""), due_date: str = Form("")):
    user = auth.current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=303)
    baby_name = baby_name.strip()[:40]
    if due_date:
        try:
            dt.date.fromisoformat(due_date)
        except ValueError:
            return templates.TemplateResponse(request, "settings.html", {
                **get_profile_safe(user), "username": user["username"],
                "welcome": "", "error": "That due date doesn't look valid."}, status_code=400)
    with get_db() as db:
        save_profile(db, user["id"], baby_name, due_date or None)
    return RedirectResponse("/", status_code=303)


def get_profile_safe(user):
    with get_db() as db:
        return get_profile(db, user["id"])

@app.get("/health")
async def health():
    return {"status": "ok"}
