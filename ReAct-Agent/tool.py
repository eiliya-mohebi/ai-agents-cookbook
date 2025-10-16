import json
from typing import Callable
import inspect


def get_fn_signature(func):
    type_map = {
        int: "integer",
        float: "number",
        str: "string",
        bool: "boolean",
        list: "array",
        dict: "object",
        type(None): "null",
    }

    name = func.__name__
    description = inspect.getdoc(func) or ""
    signature = inspect.signature(func)

    properties = {}
    required = []

    for param_name, param in signature.parameters.items():
        param_type = param.annotation

        if param.default is inspect.Parameter.empty:
            required.append(param_name)

        json_type = type_map.get(param_type, "string")

        properties[param_name] = {"type": json_type}

    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description.strip(),
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
                "additionalProperties": False,
            },
            "strict": True,
        },
    }


def validate_arguments(tool_call: dict, tool_signature: dict) -> dict:
    json_to_python_type_map = {
        "integer": int,
        "string": str,
        "boolean": bool,
        "number": float,
        "null": type(None),
    }

    properties = tool_signature["function"]["parameters"]["properties"]

    for arg_name, arg_value in tool_call["arguments"].items():
        if arg_name not in properties:
            continue

        expected_json_type = properties[arg_name].get("type")
        expected_python_type = json_to_python_type_map.get(expected_json_type)

        if expected_python_type is None:
            print(
                f"Warning: Unknown JSON type '{expected_json_type}' for argument '{arg_name}'. Skipping validation/conversion."
            )
            continue

        if not isinstance(arg_value, expected_python_type) and arg_value is not None:
            try:
                if expected_python_type is float and isinstance(arg_value, (int, str)):
                    converted_value = float(arg_value)
                elif expected_python_type is int and isinstance(arg_value, str):
                    converted_value = int(arg_value)
                elif expected_python_type is bool and isinstance(arg_value, str):
                    if arg_value.lower() in ("true", "1"):
                        converted_value = True
                    elif arg_value.lower() in ("false", "0"):
                        converted_value = False
                    else:
                        raise ValueError(
                            f"Cannot convert string '{arg_value}' to boolean."
                        )
                else:
                    converted_value = expected_python_type(arg_value)

                tool_call["arguments"][arg_name] = converted_value

            except (ValueError, TypeError) as e:
                raise ValueError(
                    f"Invalid argument value for '{arg_name}': Expected type "
                    f"'{expected_json_type}' but could not convert value "
                    f"'{arg_value}' (current type {type(arg_value).__name__}). Error: {e}"
                )

    return tool_call


class Tool:
    def __init__(self, name: str, fn: Callable, fn_signature: str, is_async: bool):
        self.name = name
        self.fn = fn
        self.fn_signature = fn_signature
        self.is_async = is_async

    def __str__(self):
        return self.fn_signature

    def run(self, **kwargs):
        return self.fn(**kwargs)


def tool(fn: Callable):
    def wrapper():
        fn_signature = get_fn_signature(fn)
        is_async = inspect.iscoroutinefunction(fn)
        return Tool(
            name=fn_signature.get("function").get("name"),
            fn=fn,
            fn_signature=json.dumps(fn_signature),
            is_async=is_async,
        )

    return wrapper()
