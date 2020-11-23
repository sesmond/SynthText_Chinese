import json
import logging
from json import JSONDecodeError
import os

logger = logging.getLogger(__name__)


def json_deserialize(json_data, obj, ignore_null=False):
    """
    反序列化为自定义对象
    :param json_data:
    :param obj:
    :param ignore_null: 如果json中不存在则忽略赋值，取对象默认值
    :return:
    """
    logger.debug("Got json data:%d bytes", len(json_data))
    try:
        data = json_data.decode('utf-8')
        data = data.replace('\r\n', '')
        data = data.replace('\n', '')
        data = json.loads(data)
        if len(json_data) < 500:
            logger.info("参数：%r", data)
    except JSONDecodeError as e:
        logger.error("JSon数据格式错误:%r", data)
        raise Exception("JSon数据格式错误:" + str(e))
    if ignore_null:
        dic2class_ignore(data, obj)
    else:
        dic2class(data, obj)


#
def request2dict(request):
    str_data = request.get_data()
    data = str_data.decode('utf-8')
    try:
        data = data.replace('\r\n', '')
        data = data.replace('\n', '')
        data = json.loads(data)
    except JSONDecodeError as e:
        logger.error(data)
        logger.error("JSon数据格式错误")
        raise Exception("JSon数据格式错误:" + str(e))
    return data


def dic2class(py_data, obj):
    """
    已经转成dict的数据转成自定义独享
    :param py_data: dict格式
    :param obj: 自定义对象
    :return:
    """
    for name in [name for name in dir(obj) if not name.startswith('_')]:
        if name not in py_data:
            setattr(obj, name, None)
        else:
            value = getattr(obj, name)
            setattr(obj, name, set_value(value, py_data[name]))


def dic2class_ignore(py_data, obj):
    """
    已经转成dict的数据转成自定义对象
    :param py_data: dict格式
    :param obj: 自定义对象
    :return:
    """
    for name in [name for name in dir(obj) if not name.startswith('_')]:
        if name not in py_data:
            # logger.debug("%r json中不存在，忽略，取默认值", name)
            # setattr(obj, name, obj.name)
            pass
        else:
            value = getattr(obj, name)
            setattr(obj, name, set_value(value, py_data[name], ignore_null=True))


def set_value(value, py_data, ignore_null=False):
    if str(type(value)).__contains__('.'):
        # value 为自定义类
        if ignore_null:
            dic2class_ignore(py_data, value)
        else:
            dic2class(py_data, value)
    elif str(type(value)) == "<class 'list'>":
        # value为列表
        if value.__len__() == 0:
            # value列表中没有元素，无法确认类型
            value = py_data
        else:
            # value列表中有元素，以第一个元素类型为准
            child_value_type = type(value[0])
            if isinstance(child_value_type, type):
                # 如果是type 则实例化
                child_value_type = value[0]
            value.clear()
            for child_py_data in py_data:
                child_value = child_value_type()
                child_value = set_value(child_value, child_py_data)
                value.append(child_value)
    else:
        value = py_data
    return value


def obj2json(obj):
    """
    复杂结构转json
    :param obj:
    :return: dict结构
    """
    result = json.dumps(obj, ensure_ascii=False, default=lambda o: o.__dict__, sort_keys=False,
                        indent=4)
    return json.loads(result)


def print_json(data):
    print(json.dumps(data, sort_keys=True, indent=4, separators=(', ', ': '), ensure_ascii=False))


def check_path(path):
    if not os.path.exists(path):
        print("路径不存在并创建：", path)
        os.makedirs(path)


def write_json(output_path, file_name, result):
    # 写 message
    pure_name = os.path.splitext(os.path.basename(file_name))[0]
    json_name = pure_name + ".json"
    json_path = os.path.join(output_path, json_name)
    check_path(output_path)
    with open(json_path, 'w', encoding='utf-8') as f1:
        json.dump(result, f1, ensure_ascii=False, default=lambda x: x.__dict__, sort_keys=False, indent=2)


def get_json_path(output_path, file_name):
    pure_name = os.path.splitext(os.path.basename(file_name))[0]
    json_name = pure_name + ".json"
    json_path = os.path.join(output_path, json_name)
    return json_path


def read_json(output_path, file_name):
    json_file = get_json_path(output_path, file_name)
    if os.path.exists(json_file):
        with open(json_file, 'r') as f:
            result = json.load(f)
        return True, result
    else:
        return False, None
