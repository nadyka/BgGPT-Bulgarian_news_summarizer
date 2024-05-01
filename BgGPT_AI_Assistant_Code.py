# Chat with an intelligent assistant in your terminal
from openai import OpenAI

#news article summarization
Article_Summarization = """Summarize this article in 5 sentences in Bulgarian... Министерският съвет одобри в сряда сключването на десетгодишен договор между АЕЦ "Козлодуй" и американската компания "Уестингхаус" (Westinghouse) за доставка на свежо ядрено гориво за V блок на ядрената централа, научи Mediapool от свои източници.

Контрактът ще е за доставка на минимум 420 касети свежо ядрено гориво годишно като първата доставка ще е през април 2024 г.. "Уестингхаус" освен това ще осигури и всички необходими системи за контрол и поддръжка на безопасността на реактора.

По-късно от енергийното министество обявиха официално, че договорът ще бъде подписан в четвъртък от шефа на АЕЦ "Козлодуй" Георги Кирков и Азиз Даг, управляващ директор на "Уестингхаус Електрик Швеция".

"Споразумението е в изпълнение на съгласуваната с Агенцията по доставките (ESA) към ЕВРАТОМ програма на АЕЦ "Козлодуй" за диверсификация на доставките на свежо ядрено гориво и в съответствие с решението на Народното събрание на Република България от 09.11.2022 г. за ускоряване на процеса за осигуряване на алтернативен доставчик", посочват от енергийното ведомство.

Подобно споразумение се подготвя и с френската "Фраматом" (Framatome) за доставка на гориво за VІ блок на АЕЦ "Козлодуй". С това ще се постигне пълна диверсификация и сигурност на доставките, потвърждават от министерството твърденията сред ядрения бранш, че новите доставки на свежото ядрено гориво ще бъдат поделени между "Уестингхаус" и "Фраматом".

Това е единственият вариант за внедряване на американското ядрено гориво в АЕЦ "Козлодуй", тъй като VІ блок работи с несъвместимо руско гориво ТВСА-12. Предлаганото от "Фраматом" гориво също е ТВСА-12 и ако беше взето решение за зареждане в V блок, това би означавало пълно отрязване на "Уестингхаус".

Така доставките на ТВЕЛ се поемат от двама от останалите световни доставчици на свежо ядрено гориво. Това на "Фраматом" всъщност е по лиценз на ТВЕЛ и представлява пълен аналог на руските касети ТВСА-12.

Горивото на "Уестингхаус" обаче все още не е лицензирано от българската Агенция за ядрено регулиране за съвместимост за работа с руското, тъй като презареждането на реакторите става с подмяната на една четвърт от горивото. Регулаторът трябва да се произнесе съвместната работа е безопасна, което трябва да стане на базата на все още изготвяни анализи от "Уестингхаус". Съгласно сключен с ядрената централа договор тези анализи трябва да са напълно готови през есента на 2023 г., като одобряването им от ядрения регулатор отнема девет месеца.

Предстои да се види какви ще са параметрите и условията на договора, който се очаква да бъде официално сключен в четвъртък.

Специалисти коментираха преди време пред Mediapool, че ключова за смяната на горивото в V блок с такова на "Уустингхаус" е системата за вътрешно-реакторен контрол на реактора, която е на руския Курчатовски институт, който трябва да зададе изходните данни на всяка от касетите, които се сменят веднъж годишно в реактора. Американската компания обаче има забрана от Агенцията за национална сигурност на САЩ да даде тези данни на руснаците, а те на свой ред отказват да предоставят достъп до системата. Проблемът е решим с изграждането на нова система за вътрешно-реакторен контрол, което и явно се крие зад формулировката за осигуряване на всички необходими системи за контрол и безопасност.

През октомври слубежният министър Росен Христов беше казал, че ще се обяви търг за избор на доставчик на свежо ядрено гориво и условията му се подготвят от "Българския енергиен холдинг", но вместо това е било взето политическото решение да се проведят отделни разговори с двата потенциални доставчика."""




# Point to the local server
client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

history = [
    {"role": "system", "content": "You are an intelligent assistant. You always provide well-reasoned answers that are both correct and helpful."},
    {"role": "user", "content": "Summarize this article in Bulgarian in 5 sentences ... " + Article_Summarization},
]

while True:
    completion = client.chat.completions.create(
        model="INSAIT-Institute/BgGPT-7B-Instruct-v0.2-GGUF",
        messages=history,
        temperature=0.7,
        stream=True,
    )

    new_message = {"role": "assistant", "content": ""}
    
    for chunk in completion:
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)
            new_message["content"] += chunk.choices[0].delta.content

    history.append(new_message)
    
    # Uncomment to see chat history
    # import json
    # gray_color = "\033[90m"
    # reset_color = "\033[0m"
    # print(f"{gray_color}\n{'-'*20} History dump {'-'*20}\n")
    # print(json.dumps(history, indent=2))
    # print(f"\n{'-'*55}\n{reset_color}")

    print()
    history.append({"role": "user", "content": "Summarize this article in Bulgarian in 5 sentences ... " + Article_Summarization})