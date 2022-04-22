def main():
    response = requests.get(API_URL, params=PARAMS)
    response_json = response.json()

    for (i, article) in enumerate(response_json["articles"]):
        print(f"Article {i}: {article['title']}")

        article = {
            "title": str(article["title"]),
            "description": str(article["description"]),
            "image_url": str(article["urlToImage"]),
            "source": article["source"],
            "date": str(article["publishedAt"]),
        }

        page = Page(data=article, size=SIZE)
        page.mode7()
        page.build_top_bar(bg_colour="black", txt_colour="random")
        page.build_bottom_bar(bg_colour="black", txt_colour="random")
        page.clean_buffer()

        assert page.output.size == (SIZE, SIZE)
        assert page.output.mode == "RGB"

        if args.show:
            page.output.show()
        if args.save:
            page.output.save(f"{OUTPUT_DIR}/news-{page.image_name}.png", "PNG")


if __name__ == "__main__":
    import requests
    from teletextify import Page
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Teletext Generator")
    parser.add_argument("--size", type=int, default=512)
    parser.add_argument("--api-key", type=str)
    parser.add_argument("--query", type=str, default="Climate Change")
    parser.add_argument("--number", type=int, default=1)
    parser.add_argument("--out_dir", type=str, default="./images")
    parser.add_argument("--save", type=bool, default=True)
    parser.add_argument("--show", type=bool, default=False)
    args = parser.parse_args()

    SIZE = args.size
    OUTPUT_DIR = args.out_dir
    API_URL = "https://newsapi.org/v2/everything?"
    PARAMS = {
        "q": args.query,
        "pageSize": args.number,
        "apiKey": args.api_key,
    }

    main()
