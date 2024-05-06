{
    'name': 'Uninstall Trigger POS',
    'description': 'Uninstall Trigger POS',
    'version': '16.0.0.0',
    'summary': 'Uninstall Trigger POS',
    'website': 'https://digitile.com',
    'depends': ['das_digitile'],
    'data': [
        "data/trigger.xml"
    ],
    "author": "Digitile",
    "uninstall_hook":"test_uninstall_hook",
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}