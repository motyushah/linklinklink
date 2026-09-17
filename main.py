
Да. Но тебе не обязательно начинать с AI-агента. Для твоей задачи лучше разделить две вещи:

AI-мозг — придумывает темы, исследует, пишет в твоём tone of voice, решает, какой визуал нужен

automation pipeline — запускает всё по расписанию, собирает картинку, отправляет на approve и публикует

Полноценный агент понадобится уже тогда, когда ты захочешь, чтобы система сама решала, о чём писать, смотрела прошлые результаты и корректировала контент-стратегию.

Что я бы собрал тебе
Примерно такую машину:

каждый понедельник / среду / пятницу

контент-стратегия
→ выбор темы
→ research
→ пост в стиле Матвея
→ корректура
→ генерация визуала
→ preview
→ approve
→ LinkedIn
→ сбор статистики
→ обучение следующего поста

Причём первые недели я оставил бы один человеческий клик перед публикацией. Не потому что технически нельзя сделать полный autopilot, а потому что личный LinkedIn — это твоя репутация. Лучше:

AI сделал всё → прислал тебе → ты нажал approve

а не проснуться и увидеть, что робот ночью решил написать «5 things Agile taught me about life».

Самый простой вариант — прямо вокруг ChatGPT
Я уже нашёл тебе две подходящие интеграции, которые можно подключить прямо здесь:

Canva — чтобы я мог брать твой шаблон, менять текст, изображения и собирать визуалы

Metricool — чтобы работать с контент-планом, аналитикой и scheduled posts

Я вывел тебе их подключение выше.

Тогда workflow может выглядеть буквально так:

«сделай следующий пост из серии AI for PMs в моём стиле. Используй наш LinkedIn-шаблон. Подготовь visual + caption и поставь на четверг 11:00»

И мы постепенно сведём это почти к одной команде.

Более серьёзный вариант — Make.com
Вот это уже практически твоя content factory.

Make сейчас умеет напрямую работать с LinkedIn, включая Create User Image Post, Create User Text Post и Create User Video Post для личного профиля. 

Я бы сделал такой сценарий:

SCHEDULE
↓
Google Sheet / Notion
↓
OPENAI
↓
topic selection
↓
research
↓
post generation
↓
tone-of-voice editor
↓
visual copy generation
↓
CANVA / image template
↓
approval
↓
LINKEDIN
↓
analytics
↓
content database
Например, в Google Sheet одна строка:

date	pillar	idea	status	post	image	approved	linkedin
21.09	AI × PM	AI intake	idea	—	—	false	—
После запуска сценария всё остальное появляется автоматически.

Я бы ещё добавил Buffer
У Buffer как раз в мае 2026 появился новый публичный API, рассчитанный в том числе на AI agents, Make, Zapier и n8n. Он умеет создавать, планировать и публиковать контент. 

Причём у Buffer есть MCP-интеграция: AI-ассистент может получить команду вроде:

draft a LinkedIn post and schedule it for Thursday

и отправить публикацию в Buffer. 

Buffer поддерживает для LinkedIn personal profiles публикацию, scheduling, картинки, PDF/carousels, видео и аналитику. 

То есть получается ещё приятнее:

Я
↓
Buffer
↓
LinkedIn
а Make занимается всей логикой вокруг.

А где здесь AI-агент?
Вот здесь начинается самое интересное.

Обычная automation говорит:

каждую среду возьми следующую строку → напиши текст → опубликуй

А agent получает более широкую задачу:

веди LinkedIn Матвея Шахурдина как контент-стратег
цель — позиционировать его как Senior Project / Delivery Manager с сильным AI/process background
публикуй 3 качественных материала в неделю
не повторяй темы
анализируй статистику предыдущих публикаций
отслеживай актуальные темы AI × Project Management
сохраняй tone of voice
предлагай эксперименты

И дальше агент сам может решить:

последние 3 поста про Agile
↓
слишком много одной темы

пост про AI automation
↓
engagement выше среднего

решение
↓
следующий пост:
"я сделал AI-агента, который превращает messy brief в нормальную PM-задачу"
Вот для этого уже нужен агент.

Как бы я сделал конкретно тебе
Не стал бы сразу городить отдельное приложение.

Я бы собрал V1 за несколько компонентов:

ChatGPT — мозг

Здесь храним твою контент-стратегию, стиль, удачные посты, forbidden AI phrases, карьерное позиционирование и content pillars

Google Sheets — база

идеи → drafts → published → статистика

Google Drive у тебя уже подключён к ChatGPT, поэтому с этой базой я смогу работать напрямую

Canva — visual engine

один хороший master-template твоей айдентики

Я не рекомендую каждый раз «генерировать картинку AI с нуля». Для твоего LinkedIn гораздо лучше:

стабильный дизайн + AI-generated content

Так профиль будет выглядеть как единая система

Make — automation layer

Metricool или Buffer — publishing layer

LinkedIn — конечная публикация

Сам LinkedIn официально позволяет приложениям публиковать от имени пользователя через разрешение w_member_social. 

И получится примерно вот что
Допустим, ночью система запускается.

01:00

Агент смотрит content backlog.

Выбирает:

почему хороший PM не должен превращать Jira в кладбище задач

Исследует тему.

Пишет черновик.

Проверяет:

нет AI-slop

нет not only... but

нет длинных тире

нормальный human English

соответствует твоему позиционированию

не повторяет предыдущие посты

Потом делает:

IMAGE

jira is not your project management system

в твоей визуальной айдентике.

И caption.

В 09:00 тебе прилетает:

POST READY
preview

Approve / Rewrite / Skip

Ты нажимаешь Approve.

И публикация сама уходит, например, в 11:30.

После этого агент через 24–72 часа записывает:

views / likes / comments / engagement

и учитывает это дальше.

Где мы сейчас
По сути, большая часть компонентов для этого уже существует. Make напрямую поддерживает пользовательские LinkedIn image posts, а Buffer в 2026 специально открыл API для AI/automation workflows. 

Поэтому я бы не писал своего агента с нуля.

V1 я бы сделал:

ChatGPT + Google Sheets + Canva + Metricool

а если автоматизация станет сложнее:

ChatGPT/OpenAI API + Make + Canva + Buffer + LinkedIn

И вот второй вариант уже будет практически автономной редакцией из одного человека — тебя.


c2dbc79d-23f2-4105-85e6-ffe007991683.png


Запись экрана — 2026-09-17 в 16.29.52.mov
Файл

Снимок экрана — 2026-09-17 в 16.32.27.png

Снимок экрана — 2026-09-17 в 16.34.54.png

e4017fe8-56c3-42e5-b431-fa2c6152821c.png

a611737e-8c84-4c3c-add2-ab84e0742ac9.png

b0df5edc-3efe-4029-ac30-8c1ed906d5fd.png
вроде вышло 

f22da525-cd41-4d8a-bd62-29af51853ae8.png

carousel-1.png
carousel-2.png
carousel-3.png
carousel-4.png
carousel-5.png
day8-1.png
day8-2.png
day8-3.png
day8-4.png
day8-5.png
day8-6.png
(1) i think a project manager is basically a parent to their projects 👨‍🍼 

(yes, i know. you’re not supposed to call your projects your babies. you’re supposed to stay emotionally detached, make rational decisions, look at the triangle, update the spreadsheet and move on)

but hear me out 🗣️ 🗣️ 🗣️ 

every project is basically a child at a different stage of development:
- one can’t even hold its head up yet, so you have to support it constantly;
- one just filled its diaper and needs immediate attention;
- one is sick and you’re already calling an ambulance;
- one is running around the room screaming for absolutely no apparent reason; - and one is quietly sitting at the table doing a puzzle and, for once, you can leave it alone for 20 minutes

projects and teams are pretty much the same. some need structure, some need freedom, some need constant attention, and some need you to stop touching them and let people do their jobs

figuring out which one you’re dealing with is probably as important as knowing your scope, budget, timeline and risks 
there’s a surprisingly pedagogical and psychological side to project management that doesn’t really fit into the classic project management triangle

so yeah, stock up on diapers, wet wipes and rattles. we’ve got projects to deliver 💨

(2) i would like to introduce a new management methodology:

LOW CORTISOL MANAGEMENT™ 🧚 
does it exist?

hell nah 💀 

i mean, theoretically, a low cortisol project is possible
you just need:

- decision-makers who know what they want;
- stakeholders who can explain what they want;
- enough budget, people and time to do it;
- timelines that can move when reality happens;
- a motivated team that wants to ship;
- self-driven people with golden hands;
- a healthy connection between the team and stakeholders

basically, you just need everything to go right at the same time

easy
you have achieved LOW CORTISOL MANAGEMENT™ 🧚 
in approximately 1 out of 1,000 projects

the other 999 have their own drama
but project management is about making sure the project keeps moving when cortisol starts going up

so put on your armor
we’re bulletproof, nothing to lose 🦺

(3) every project plan should have a backflip built into it 🤸

you start a project, build a beautiful timeline, plan the roadmap, book the right people, distribute the workload, align everyone on priorities

everything fits. beautiful 👍 

and then suddenly everything that was a priority yesterday is not a priority anymore
new priority, new scope, sometimes a completely new goal. and suddenly the whole team has to do a backflip at the same time
re-prioritize, re-brief, re-plan, re-book people, figure out what stays, what moves and what dies

this is not really an exception. the possibility of a backflip should probably be built into the project from day one

because priorities will change, scope will change, people will change their minds. and sometimes the thing everyone agreed was extremely important on monday is somehow completely irrelevant by thursday

you can’t really prevent that. you can only make sure the team knows how to flip together

and the project manager’s job is to put enough gym mats on the floor so even if someone lands on their neck, everyone stays alive 🫡

(4) starting a series: one day, one PM problem, one working automation.
building each one myself, showing what's inside

day 1 — jira deadlines, straight to telegram

09:00 every day, one message: everything overdue, everything due
today, everything due in the next three days. sorted by how much
it burns. red, orange, yellow. nothing else in it

four nodes. schedule → jira → code → telegram
the filter does the actual work:

project = DR AND statusCategory != Done AND due <= 3d
ORDER BY due ASC

statusCategory, not status – statuses get renamed, categories don't.
that one word is the difference between a filter that works and a
filter that quietly breaks in six months

—

why this one first: a board never tells you when something is about
to slip. you have to go and look. which is fine on a calm week. on a
loud one it's the first thing that drops, and you find out a task was
overdue two days ago from the person who was waiting on it

fair warning on the numbers: this runs on a test project with six
issues, not a live team. I'm not going to tell you it saved X hours.
what I can say is the check now happens whether I remember it or not

what do you check by hand every morning that could check itself?

(5) pm basics #1

on an interview I was asked what is scrum, what is agile

I said scrum is to agile what a species is to a genus. correct, and I had nothing behind it. four years working in agile methodologies and I couldn't actually explain the thing

so I went and figured it out properly

погоди, сейчас еще скину 

s-01.png
s-02.png
s-03.png
s-04.png
s-05.png
s-06.png
s-07.png
s-08.png
s-09.png
еще погоди 

Да. Если репозиторий Public, то любой человек может открыть его и увидеть код, историю коммитов и всё, что ты туда коммитишь

Я посмотрел именно тот код, который тебе дал. API-ключи там не лежат — они берутся из GitHub Secrets, то есть публично не показываются

Но есть два нюанса:

в коде есть твоё имя, сайт motyushah.com, описание опыта и правила твоего tone of voice

все сгенерированные карусели код сейчас коммитит в папку generated/. Значит, они тоже будут публично доступны через GitHub, даже если это просто черновики, которые ты потом не выберешь

То есть прям критичной сенситивной информации там сейчас нет: нет паролей, банковских данных, адреса, паспорта, зарплаты и т.п. Но твои будущие неопубликованные посты/карусели будут фактически публичными файлами

И ещё важное правило: никогда не вставляй API-ключ прямо в main.py. Только GitHub Secrets. Если ключ хоть раз попадёт в публичный commit, даже если потом его удалить, считай его скомпрометированным и меняй

Для твоего кейса я бы лучше не делал repo Public вообще. Можно оставить его Private и вынести картинки в отдельное бесплатное публичное хранилище, чтобы Buffer видел только изображения, а код и черновики оставались приватными

Это безопаснее и правильнее. Могу сейчас переделать схему именно так, без доплаты.


ee343133-b556-4004-85a0-160ca1390cee.png

вижу. Тут код не сломался — Gemini на всех трёх моделях ответил 503 Service Unavailable. Google прямо определяет 503 как временную перегрузку/недоступность и советует повторять запрос с увеличивающейся паузой. 

И я бы сейчас сделал ещё одну вещь: для нового проекта поставил gemini-3.5-flash первым запасным вариантом. Google сам рекомендует новым проектам 3.5 Flash или 3.1 Flash-Lite. 

В main.py найди внутри generate_candidates вот это:

models = [
    "gemini-3.8-flash",
    "gemini-3.7-flash",
    "gemini-3.6-flash",
]
и замени на:

models = [
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-3.8-flash",
]
И чуть ниже найди:

time.sleep(5 * (attempt + 1))
замени на:

time.sleep(15 * (attempt + 1))
Commit changes → Run workflow ещё раз

Больше пока ничего не трогай. Если снова все четыре модели дадут 503, тогда дело уже в текущей доступности Gemini для твоего free-проекта, и я переключу нашу машину на другой бесплатный AI endpoint, не ломая Buffer и генерацию картинок.


Нет, слишком сложно для меня. сразу весь готовый код скинь, который надо переставить.

да, проще: ничего руками внутри кода не меняй

я уже собрал тебе полностью готовый main.py, где:

сначала пробуются бесплатные Gemini-модели

если одна отдаёт 503, скрипт ждёт и пробует снова

потом автоматически переключается на следующую

остальная логика с каруселями и Buffer остаётся как была

Google сейчас действительно даёт free tier для gemini-3.5-flash и gemini-3.5-flash-lite. 

Скачай файл:

готовый main.py

Дальше только:

GitHub → Code

открыть main.py

нажать карандаш

удалить всё

вставить содержимое скачанного файла

Commit changes

Actions → Run workflow

run.yml не трогай

Если снова упадёт — просто кидай скрин ошибки, без самостоятельных правок.


main_ready.py
Код


Библиотека
/
main_ready.py


519
520
521
522
523
524
525
526
527
528
529
530
531
532
533
534
535
536
537
538
539
540
541
542
543
544
545
546
547
548
549
550
551
552
553
554
555
556
557
558
559
560
561
562
563
564
565
566
567
568
569
570
571
572
573
574
575
576
577
578
579
580
581
582
583
584
585
586
587
588
589
590
591
592
593
594
595
596
597
598
599
600
601
602
603
604
605
606
607
608
609
610
611


def public_url(path):
    repo = os.environ["GITHUB_REPOSITORY"]
    branch = os.environ.get("GITHUB_REF_NAME", "main")
    rel = path.relative_to(ROOT).as_posix()
    return f"https://raw.githubusercontent.com/{repo}/{branch}/{rel}"

def wait_until_public(url):
    for _ in range(12):
        try:
            r = requests.get(url, timeout=15)
            if r.status_code == 200 and r.content:
                return
        except Exception:
            pass
        time.sleep(5)
    raise RuntimeError(f"generated image did not become public: {url}")

def create_buffer_draft(channel_id, text, urls):
    assets = [{"image": {"url": u}} for u in urls]
    data = buffer_request(
        """
        mutation CreateDraft($input: CreatePostInput!) {
          createPost(input: $input) {
            ... on PostActionSuccess {
              post { id text }
            }
            ... on MutationError {
              message
            }
          }
        }
        """,
        {
            "input": {
                "text": text,
                "channelId": channel_id,
                "schedulingType": "automatic",
                "mode": "addToQueue",
                "saveToDraft": True,
                "aiAssisted": True,
                "assets": assets,
            }
        },
    )
    result = data["createPost"]
    if result.get("message"):
        raise RuntimeError(result["message"])
    return result["post"]

def main():
    download(ANTON_URL, ANTON)
    download(INTER_URL, INTER)

    channel_id = get_linkedin()
    trends = collect_trends()
    posts = generate_candidates(make_prompt(trends))

    run_id = os.getenv("GITHUB_RUN_ID", str(int(time.time())))
    run_dir = ROOT / "generated" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    rendered = []
    for p_idx, post in enumerate(posts, start=1):
        post_dir = run_dir / f"post_{p_idx:02d}"
        post_dir.mkdir(parents=True, exist_ok=True)
        slides = post.get("carousel", {}).get("slides", [])[:8]
        if len(slides) < 2:
            raise RuntimeError("carousel needs at least 2 slides")
        slides[-1]["signature"] = True

        paths = []
        for s_idx, slide in enumerate(slides):
            out = post_dir / f"slide_{s_idx + 1:02d}.png"
            render_slide(slide, s_idx, out)
            paths.append(out)
        rendered.append((post, paths))

    # Buffer needs public URLs, so publish the generated PNG files first.
    git_publish_generated()

    for post, paths in rendered:
        urls = [public_url(p) for p in paths]
        wait_until_public(urls[0])
        created = create_buffer_draft(channel_id, post["text"].strip(), urls)
        print("BUFFER DRAFT:", created["id"])
        print("MEDIA:", len(urls))

    print(f"DONE: {len(rendered)} drafts with carousels created")

if __name__ == "__main__":
    main()

