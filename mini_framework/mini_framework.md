# Mini Framework

mini_framework  
├── configurations  
│   ├── __init__.py  
│   ├── config_base.py  
│   └── config_manager.py  
├── databases  
│   ├── __init__.py  
│   ├── config.py  
│   ├── conn_managers  
│   │   ├── __init__.py  
│   │   ├── conn_metrics.py  
│   │   ├── db_manager.py  
│   │   ├── load_balancer.py  
│   │   ├── session.py  
│   │   ├── tenant_db.py  
│   │   └── utilities.py  
│   ├── dao_gen_command.py  
│   ├── entities  
│   │   ├── __init__.py  
│   │   ├── dao_base.py  
│   │   ├── declaritives.py  
│   │   └── toolkit.py  
│   ├── queries  
│   │   ├── __init__.py  
│   │   ├── errors.py  
│   │   └── pages.py  
│   ├── toolkit  
│   │   ├── __init__.py  
│   │   ├── dao_generator.py  
│   │   ├── generator_models  
│   │   │   ├── __init__.py  
│   │   │   ├── add.py  
│   │   │   ├── count.py  
│   │   │   ├── delete.py  
│   │   │   ├── get_by_pk.py  
│   │   │   ├── operator.py  
│   │   │   ├── page.py  
│   │   │   └── update.py  
│   └── version  
│       └── __init__.py  
├── storage  
│   ├── __init__.py  
│   ├── config.py  
│   ├── errors.py  
│   ├── manager.py  
│   ├── persistent  
│   │   ├── __init__.py  
│   │   ├── file_storage_dao.py  
│   │   └── models.py  
│   └── view_model.py  
├── web  
│   ├── __init__.py  
│   ├── api_doc_manager.py  
│   ├── app_context.py  
│   ├── middlewares  
│   │   ├── __init__.py  
│   │   ├── auth.py  
│   │   ├── base.py  
│   │   ├── cache.py  
│   │   ├── database.py  
│   │   ├── limit.py  
│   │   └── log.py  
│   ├── request_context.py  
│   ├── router.py  
│   ├── session.py  
│   ├── std_models  
│   │   ├── __init__.py  
│   │   ├── account.py  
│   │   └── page.py  
│   ├── toolkit  
│   │   ├── __init__.py  
│   │   ├── login_state.py  
│   │   └── model_utilities.py  
│   ├── views.py  
│   └── web_command.py  
├── utils  
│   ├── __init__.py  
│   ├── data_secure.py  
│   ├── http.py  
│   ├── json.py  
│   ├── logging.py  
│   ├── modules.py  
│   ├── retry.py  
│   └── time.py  
├── authentication  
│   ├── __init__.py  
│   ├── auth_rule.py  
│   ├── jwt.py  
│   ├── oauth2.py  
│   ├── persistent  
│   │   ├── __init__.py  
│   │   ├── auth_dao.py  
│   │   └── jwt_daos.py  
│   └── rules  
│       ├── __init__.py  
│       ├── auth_rule.py  
│       └── jwt_rule.py  
├── async_task  
│   ├── __init__.py  
│   ├── app  
│   │   ├── __init__.py  
│   │   ├── app.py  
│   │   ├── app_factory.py  
│   │   └── context.py  
│   ├── async_task_command.py  
│   ├── consumers  
│   │   ├── __init__.py  
│   │   ├── consumer.py  
│   │   ├── context.py  
│   │   ├── database_executor.py  
│   │   ├── event_type.py  
│   │   ├── executor.py  
│   │   ├── retry.py  
│   │   └── success.py  
│   ├── data_access  
│   │   ├── __init__.py  
│   │   ├── task_dao.py  
│   │   ├── task_rule.py  
│   └── event_bus  
│       ├── __init__.py  
│       ├── event.py  
│       └── event_bus.py  
├── commands  
│   ├── __init__.py  
│   ├── cli.py  
│   └── command_base.py  
├── context  
│   ├── __init__.py  
│   └── environment.py  
├── design_patterns  
│   ├── __init__.py  
│   ├── depend_inject.py  
│   └── singleton.py  
├── message_queue  
│   ├── __init__.py  
│   ├── config.py  
│   ├── kafka_utils.py  
│   └── topic.py  
└── storage  
    ├── __init__.py  
    ├── config.py  
    ├── errors.py  
    ├── manager.py  
    ├── persistent  
    │   ├── __init__.py  
    │   ├── file_storage_dao.py  
    │   └── models.py  
    └── view_model.py  
```
