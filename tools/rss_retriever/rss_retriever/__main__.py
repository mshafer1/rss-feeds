import pathlib
import re
import typing
import click
import hashlib

import rss_retriever

@click.command
@click.option("--feed", "feeds", required=True, multiple=True)
@click.option("--items-path", help="key/path/to/items", required=True)
@click.option("--item-id-key", help="key of field to use as ID for comparison")
@click.option("--output-json", is_flag=True)
@click.option("--cache-dir", type=click.Path(file_okay=False, path_type=pathlib.Path))
@click.option("--out-dir", default=".", type=click.Path(file_okay=False, path_type=pathlib.Path))
def main(feeds: typing.Tuple[str, ...], output_json: bool, out_dir: pathlib.Path, cache_dir: pathlib.Path, items_path: str, item_id_key: typing.Optional[str]):
    cache_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    for feed in feeds:
        data = rss_retriever.fetch_feed(uri=feed, return_json=output_json, cache_dir=cache_dir, items_path=items_path, item_id_key=item_id_key)

        out_file_name = re.sub(r'[^\dA-Za-z\.\-]', '_', feed) + "." + hashlib.md5(feed.encode("ascii"), usedforsecurity=False).hexdigest()[:8]
        output_file = out_dir / (out_file_name + ('.json' if output_json else '.xml'))
        output_file.write_text(data, encoding="UTF-8")


if __name__ == '__main__':
    main()
