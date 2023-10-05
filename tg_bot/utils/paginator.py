import itertools

from aiogram.fsm.context import FSMContext


def slice_dict(start_dict: dict[str, str], num_elements: int) -> tuple [dict[str, dict[str, str]], int]:
    result_dict: dict[str, dict[str, str]] = {}
    cursor = 0
    num_pages = len(start_dict) // num_elements
    add_pager = len(start_dict) % num_elements

    for i in range(0, num_pages):
        temp_dict: dict[str: str] = dict(itertools.islice(start_dict.items(), cursor, cursor + num_elements))
        result_dict.update({str(i): temp_dict})
        cursor += num_elements


    if add_pager != 0:
        temp_dict: dict[str: str] = dict(itertools.islice(start_dict.items(), cursor, len(start_dict)))
        result_dict.update({str(num_pages): temp_dict})
        num_pages += 1

    if not result_dict:
        result_dict.update({str(0) : {}})
        num_pages = 0


    return result_dict, num_pages


async def get_current_page(state: FSMContext, is_next: bool = True):
    data = await state.get_data()
    result_dict: dict[str, dict[str, str]] = data['result_dict']
    current_page = data['current_page']
    num_pages = data['num_pages']

    if num_pages == 0:
        return result_dict[str(0)]

    if is_next:
        current_page = current_page + 1 if current_page != num_pages - 1 else 0
    else:
        current_page = current_page - 1 if current_page != 0 else num_pages - 1

    await state.update_data(current_page=current_page)

    return result_dict[str(current_page)]

