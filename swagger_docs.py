from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from drf_yasg.views import get_schema_view
from rest_framework import permissions


schema_view = get_schema_view(
   openapi.Info(
      title="API",
      default_version='v1',
      description="АПИ для тестового задания",
   ),
   public=True,
   permission_classes=(permissions.AllowAny, ),
)

desc_username_txt = 'Username'
desc_userpass_txt = 'User Password'
desc_error_msg = 'Error message'

UNAUTH_ERROR_TEXT = {
    "detail": "Given token not valid for any token type",
    "code": "token_not_valid",
    "messages": [
        {
            "token_class": "AccessToken",
            "token_type": "access",
            "message": "Token is invalid or expired"
        }
    ]
}

UNAUTH_ERROR = openapi.Response('Unauthorized',
                                openapi.Schema(type=openapi.TYPE_OBJECT,
                                               description=desc_error_msg,
                                               example=UNAUTH_ERROR_TEXT),
                                )

user_registration_schema = swagger_auto_schema(
    operation_description="Регистрация пользователя",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING,
                                       description=desc_username_txt,
                                       exapmle='KatanaNevermore'),
            'password': openapi.Schema(type=openapi.TYPE_STRING,
                                       description=desc_userpass_txt,
                                       exapmle='NevermorePassword'),
            'email': openapi.Schema(type=openapi.TYPE_STRING,
                                    description='User Email',
                                    example='example@gmail.com'),
            'referral_code': openapi.Schema(type=openapi.TYPE_STRING,
                                            description='Referal code (необязательно)',
                                            example='WETWG9RHJLZAIOAJOUN4'),
        },
    ),
    responses={
        201: openapi.Response('Created', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'message': openapi.Schema(type=openapi.TYPE_STRING,
                                          description='Success message',
                                          example=[
                                              'Successfully created a new user without referral code',
                                              'Successfully created a new user with referral code'
                                                  ]
                                          ),
            },
        )),
        400: openapi.Response('Bad Request', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING,
                                        description='Error message',
                                        example=['A user with that username already exists.',
                                                 'This field is required.']),
                'email': openapi.Schema(type=openapi.TYPE_STRING,
                                        description='Error message',
                                        example=['This field is required.']),
                'password': openapi.Schema(type=openapi.TYPE_STRING,
                                        description='Error message',
                                        example='This field is required.'),
                'error': openapi.Schema(type=openapi.TYPE_STRING,
                                        description='Error message',
                                        example=['Invalid referral code',
                                                 'Invalid email address']),
            },
        )),
    }
)

user_login_schema = swagger_auto_schema(
    operation_description="Авторизация пользователя",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING,
                                       description=desc_username_txt,
                                       example='KatanaNevermore'),
            'password': openapi.Schema(type=openapi.TYPE_STRING,
                                       description=desc_userpass_txt,
                                       example='NevermorePassword'),
        },
    ),
    responses={
        200: openapi.Response('OK', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'refresh': openapi.Schema(type=openapi.TYPE_STRING,
                                          description='Refresh token',
                                          example='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTcxMDY4MjkzOCwiaWF0IjoxNzEwNTEwMTM4LCJqdGkiOiI2ZDhiNDUzOGMyYWI0YjQ2ODNmYWI2ODRjOGQ4NDY2MiIsInVzZXJfaWQiOjF9.WaJ3C-VjmNQ5FeS0A8KBQ7pYfOjrf7St6dXOiDfTj2I'),
                'access': openapi.Schema(type=openapi.TYPE_STRING,
                                         description='Access token',
                                         example='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzEwOTQyMTM4LCJpYXQiOjE3MTA1MTAxMzgsImp0aSI6IjdjZmJlMjE1ZDViNDQ4NmM5MjU4ODFkNDExN2NkZDUwIiwidXNlcl9pZCI6MX0.WCyUu-_WsZKGYC5il5pkmvszw77X5VKdmABE94w0uok'),
            },
        )),
        400: openapi.Response('Bad Request', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'error': openapi.Schema(type=openapi.TYPE_STRING,
                                        description=desc_error_msg,
                                        example='Invalid Username/Password'),
            },
        )),
    }
)



referral_code_get_schema = swagger_auto_schema(
    operation_description="Отправка реферального кода на email реферера. Почта реферера берется автоматически.",
    responses={
        200: openapi.Response('OK',
                              openapi.Schema(type=openapi.TYPE_OBJECT,
                                             properties={'message': openapi.Schema(type=openapi.TYPE_STRING,
                                                                                   description='Success message',
                                                                                   example='Referral code has been sent to the email'),
            },
        )),
        404: openapi.Response('Not Found',
                              openapi.Schema(type=openapi.TYPE_OBJECT,
                                             properties={'message': openapi.Schema(type=openapi.TYPE_STRING,
                                                                                   description=desc_error_msg,
                                                                                   example='No active code found for this user'),
            },
        )),
        401: UNAUTH_ERROR,
    }
)



referral_code_post_schema = swagger_auto_schema(
    operation_description="Апи для создания реферального кода. Дату можно указывать в любом формате. dd.MM.yyyy/dd.MM.yy/yyyy-MM-dd",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'expiry_date': openapi.Schema(type=openapi.TYPE_STRING,
                                          description='Expiry date of the referral code',
                                          example='2024-12-31'),
        },
    ),
    responses={
        201: openapi.Response('Created', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'user': openapi.Schema(type=openapi.TYPE_INTEGER,
                                       description='User ID',
                                       example = 1),
                'code': openapi.Schema(type=openapi.TYPE_STRING,
                                       description='Referral code',
                                       example = 'RTUMA5PUO1JUI5EKHAUX'),
                'expiry_date': openapi.Schema(type=openapi.TYPE_STRING,
                                              description='Expiry date of the referral code',
                                              example = '2024-12-22'),
                'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN,
                                            description='Is the referral code active',
                                            example = True),
            },
        )),
        400: openapi.Response('Bad Request', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'error': openapi.Schema(type=openapi.TYPE_STRING,
                                        description=desc_error_msg,
                                        example='Expiry date is required or Expiry date must be in the future'),
            },
        )),
        401: UNAUTH_ERROR
    },
)

referral_code_delete_schema = swagger_auto_schema(
    operation_description="Удаление реферального кода. Удаляется последний активный реферальный код пользователя.",
    responses={
        204: openapi.Response('No Content', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'message': openapi.Schema(type=openapi.TYPE_STRING, description='Success message', example='Code successfully deleted'),
                'code': openapi.Schema(type=openapi.TYPE_OBJECT, description='Deleted referral code', properties={
                    'user': openapi.Schema(type=openapi.TYPE_INTEGER, description='User ID', example = 1),
                    'code': openapi.Schema(type=openapi.TYPE_STRING, description='Referral code', example = 'RTUMA5PUO1JUI5EKHAUX'),
                    'expiry_date': openapi.Schema(type=openapi.TYPE_STRING, description='Expiry date of the referral code', example = '2024-12-22'),
                    'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Is the referral code active', example = True),
                }),
            },
        )),
        404: openapi.Response('Not Found', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'message': openapi.Schema(type=openapi.TYPE_STRING, description=desc_error_msg, example='No active code found'),
            },
        )),
        401: UNAUTH_ERROR
    },
)

referral_code_info_schema = swagger_auto_schema(
    operation_description="Получнение данных о рефералах для реферера",
    responses={
        200: openapi.Response('OK', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'referrals': openapi.Schema(type=openapi.TYPE_OBJECT, description='Deleted referral code', example=['katana1', 'katana2'])
            },
        )),
        401: UNAUTH_ERROR
    },
)
