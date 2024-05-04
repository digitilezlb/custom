{
    'name': 'Uninstall Trigger',
    'description': 'Uninstall Trigger',
    'version': '16.0.0.0',
    'summary': 'Uninstall Trigger',
    'website': 'https://digitile.com',
    'depends': ['das_digitile','das_kitchen_notes'],
    'data': [
        "data/trigger.xml"
    ],
    "author": "Digitile",
    "uninstall_hook":"test_uninstall_hook",
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}