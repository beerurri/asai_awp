{
    'name': "ASAI AWP",
    'version': '0.1',
    'depends': ['base', 'web'],
    'application': True,
    'installable': True,
    'author': "Ivan Sergeev",
    'category': 'Uncategorized',
    'description': """
    === Description text ===
    """,
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/awp_menus.xml',
        'demo/demo_users.xml',
        'demo/docs_demo.xml',
        'demo/tasks_demo.xml',
    ],
    'post_init_hook': 'delete_from_awp_tasks_taken_by_users_rel',
    # 'demo': [
    #     'demo/docs_demo.xml',
    #     'demo/tasks_demo.xml',
    # ],
    'assets': {
        'web.assets_backend': [
            'asai_awp/static/src/js/awp_client_action.js',
            'asai_awp/static/src/css/awp_styles.css',
            'asai_awp/static/src/xml/tasks_template.xml',
            'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css',
            'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js',
        ],
        'web.assets_frontend': [
            'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css',
            'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js',
        ],
    },
}