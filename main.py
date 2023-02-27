from typing import List, Literal
from pydantic import BaseModel, parse_file_as
from jinja2 import Template


class DirectoryOkved(BaseModel):
    id: int
    code: str
    name: str


class TableRecord(BaseModel):
    """
    HTML table record model
    """
    object: DirectoryOkved
    state: Literal["unmodified", "updated", "new", "deleted"]


def get_diff(
    l1: List[DirectoryOkved],
    l2: List[DirectoryOkved]
) -> List[TableRecord]:
    """
    Get differences between two lists of objects

    Args:
        l1 (List[DirectoryOkved]): list before manipulations
        l2 (List[DirectoryOkved]): list after manipulations

    Returns:
        List[TableRecord]: list of compared objects, ready to template rendering
    """
    results = {}
    for item in l2:
        results[item.id] = {"object": item, "state": "new"}

    for item in l1:
        if not {item.id}.issubset(results):
            results[item.id] = {"object": item, "state": "deleted"}
        elif item == results[item.id]["object"]:
            results[item.id]['state'] = "unmodified"
        elif item != results[item.id]["object"]:
            results[item.id]['state'] = "updated"

    return [v for k, v in results.items()]


def render_output(
        l1: List[DirectoryOkved],
        l2: List[DirectoryOkved]
):
    """
    Render output template to file ./output.html

    Args:
        l1 (List[DirectoryOkved]): list of objects before manipulations
        l2 (List[DirectoryOkved]): list of objects after manipulations
    """
    template_name = './template.html'
    with open(template_name, 'r', encoding='utf-8') as template_fp:
        template = Template(template_fp.read())
    object_list = get_diff(l1, l2)

    with open("./output.html", "w", encoding="utf-8") as output_fp:
        output_fp.write(template.render({"object_list": object_list}))


if __name__ == "__main__":
    l1 = parse_file_as(List[DirectoryOkved], './samples/1.json')
    l2 = parse_file_as(List[DirectoryOkved], './samples/2.json')

    render_output(l1, l2)
