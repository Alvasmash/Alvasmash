import os
import requests
from collections import defaultdict

USERNAME = "Alvasmash"

# Repositorio del perfil.
# Lo excluimos porque contiene principalmente el README
# y no queremos que distorsione las estadísticas.
EXCLUDED_REPOS = {
    "Alvasmash"
}

HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
    "X-GitHub-Api-Version": "2026-03-10"
}


def get_repositories():
    repositories = []

    page = 1

    while True:
        url = (
            f"https://api.github.com/users/{USERNAME}/repos"
            f"?per_page=100&page={page}&type=owner"
        )

        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()

        data = response.json()

        if not data:
            break

        repositories.extend(data)
        page += 1

    return repositories


def get_languages(repo):
    owner = repo["owner"]["login"]
    name = repo["name"]

    url = f"https://api.github.com/repos/{owner}/{name}/languages"

    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        print(f"No se pudieron obtener lenguajes de {name}")
        return {}

    return response.json()


def main():

    print("Buscando repositorios de", USERNAME)

    repositories = get_repositories()

    total_languages = defaultdict(int)

    for repo in repositories:

        repo_name = repo["name"]

        # Ignorar forks
        if repo["fork"]:
            print(f"Ignorando fork: {repo_name}")
            continue

        # Ignorar repositorio del perfil
        if repo_name in EXCLUDED_REPOS:
            print(f"Ignorando perfil: {repo_name}")
            continue

        print(f"Analizando: {repo_name}")

        languages = get_languages(repo)

        for language, bytes_count in languages.items():
            total_languages[language] += bytes_count

    total_bytes = sum(total_languages.values())

    if total_bytes == 0:
        print("No se encontraron lenguajes.")
        return

    # Ordenar de mayor a menor
    languages_sorted = sorted(
        total_languages.items(),
        key=lambda x: x[1],
        reverse=True
    )

    print("\n=== RESULTADO ===")

    for language, bytes_count in languages_sorted:
        percentage = (bytes_count / total_bytes) * 100
        print(f"{language}: {percentage:.2f}%")

    generate_svg(languages_sorted, total_bytes)


def generate_svg(languages, total_bytes):

    # Mostrar los 10 lenguajes principales
    languages = languages[:10]

    width = 900
    row_height = 72
    height = 170 + (len(languages) * row_height)

    svg = f'''<svg width="{width}" height="{height}"
xmlns="http://www.w3.org/2000/svg">

<rect width="100%" height="100%" rx="18"
fill="#0D1117"/>

<text x="45" y="55"
font-family="Arial, sans-serif"
font-size="28"
font-weight="bold"
fill="#FFFFFF">
🩸 Lenguajes utilizados
</text>

<text x="45" y="82"
font-family="Arial, sans-serif"
font-size="14"
fill="#8B949E">
Distribución real del código en mis repositorios
</text>
'''

    y = 125

    for language, bytes_count in languages:

        percentage = (bytes_count / total_bytes) * 100

        # Ancho máximo de barra
        max_bar_width = 560

        bar_width = max_bar_width * (percentage / 100)

        # Evitar barras demasiado pequeñas
        if bar_width < 4:
            bar_width = 4

        svg += f'''
<text x="45" y="{y}"
font-family="Arial, sans-serif"
font-size="16"
font-weight="bold"
fill="#FFFFFF">
{language}
</text>

<text x="650" y="{y}"
font-family="Arial, sans-serif"
font-size="16"
font-weight="bold"
fill="#E63946">
{percentage:.2f}%
</text>

<rect x="45" y="{y + 12}"
width="560"
height="13"
rx="6"
fill="#21262D"/>

<rect x="45" y="{y + 12}"
width="{bar_width}"
height="13"
rx="6"
fill="#E63946"/>

'''

        y += row_height

    svg += '''
</svg>
'''

    os.makedirs("assets", exist_ok=True)

    with open("assets/languages.svg", "w", encoding="utf-8") as file:
        file.write(svg)

    print("\nSVG generado correctamente.")
    print("Archivo: assets/languages.svg")


if __name__ == "__main__":
    main()