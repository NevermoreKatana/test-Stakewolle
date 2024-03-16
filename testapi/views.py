import requests
import swagger_docs 
from rest_framework.request import Request
from dateutil import parser
from testapi.serializers import UserSerializer, ReferralCodeSerializer
from testapi.models import ReferralCode, Referral
from config import get_app_settings
from rest_framework import status, views
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.core.mail import send_mail
from django.contrib.auth import get_user_model, authenticate


SETTINGS = get_app_settings()
USER_MODEL = get_user_model()


class UserRegistrationView(views.APIView):
    """
    API-представление для регистрации пользователя.

    Это представление позволяет любому пользователю зарегистрироваться. Оно проверяет данные пользователя,
    подтверждает адрес электронной почты и создает нового пользователя. Если предоставлен действительный
    реферальный код, создается объект реферала.

    Атрибуты:
        permission_classes: Список классов разрешений, которые должно использовать представление.
    """
    
    permission_classes: list = [AllowAny]


    @swagger_docs.user_registration_schema
    def post(self, request: Request) -> Response:
        """
        Обрабатывает POST-запросы для регистрации пользователя.

        Этот метод проверяет данные пользователя с помощью UserSerializer. Если данные действительны,
        он подтверждает адрес электронной почты с помощью API hunter.io. Если адрес электронной почты действителен,
        он создает нового пользователя. Если предоставлен действительный реферальный код, он создает объект реферала.

        Аргументы:
            request: Объект запроса.

        Возвращает:
            Объект Response. Если данные пользователя и адрес электронной почты действительны, и пользователь успешно создан,
            он возвращает статус 201 и сообщение об успехе. Если адрес электронной почты или реферальный код недействителен,
            он возвращает статус 400 и сообщение об ошибке. Если данные пользователя недействительны, он возвращает статус 400 и ошибки проверки.
        """
        
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get("email")
            response = requests.get(f"https://api.hunter.io/v2/email-verifier?email={email}&api_key={SETTINGS.eh_api_key}",
                                    timeout=None)
            
            if response.json()['data'].get('status') != 'valid':
                return Response({"error": "Invalid email address"},
                                status=status.HTTP_400_BAD_REQUEST)

            referral_code = request.data.get("referral_code")
            referrer = None
            if referral_code:
                try:
                    referrer = ReferralCode.objects.get(code=referral_code).user
                except ReferralCode.DoesNotExist:
                    return Response({"error": "Invalid referral code"},
                                    status=status.HTTP_400_BAD_REQUEST)

            user = USER_MODEL.objects.create_user(**serializer.validated_data)
            if user and referrer:
                Referral.objects.create(referrer=referrer, referral=user)
                return Response({'message': 'Successfully created a new user with referral code'},
                                status=status.HTTP_201_CREATED)
            elif user:
                return Response({'message': 'Successfully created a new user without referral code'},
                                status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class UserLoginView(views.APIView):
    """
    API-представление для входа пользователя.

    Это представление позволяет любому пользователю войти в систему. Оно проверяет имя пользователя и пароль,
    аутентифицирует пользователя и, если аутентификация прошла успешно, возвращает токены обновления и доступа.

    Атрибуты:
        permission_classes: Список классов разрешений, которые должно использовать представление.
    """
    
    permission_classes: list = [AllowAny]
    
    
    @swagger_docs.user_login_schema
    def post(self, request: Request) -> Response:
        """
        Обрабатывает POST-запросы для входа пользователя.

        Этот метод получает имя пользователя и пароль из запроса, аутентифицирует пользователя и, если аутентификация
        прошла успешно, возвращает токены обновления и доступа. Если аутентификация не прошла успешно, возвращает ошибку.

        Аргументы:
            request: Объект запроса.

        Возвращает:
            Объект Response. Если аутентификация прошла успешно, возвращает статус 200 и токены обновления и доступа.
            Если аутентификация не прошла успешно, возвращает статус 400 и сообщение об ошибке.
        """
        
        username = request.data.get("username", "")
        password = request.data.get("password", "")
        user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid Username/Password'},
                        status=status.HTTP_400_BAD_REQUEST)
    

class ReferralCodeView(views.APIView):    
    """
    API-представление для работы с реферальными кодами.

    Это представление позволяет аутентифицированным пользователям получать, создавать и удалять свои реферальные коды.

    Атрибуты:
        permission_classes: Список классов разрешений, которые должно использовать представление.
    """
    
    permission_classes: list = [IsAuthenticated]


    @swagger_docs.referral_code_get_schema
    def get(self, request: Request) -> Response:
        """
        Обрабатывает GET-запросы для получения реферального кода пользователя.

        Этот метод получает активный реферальный код пользователя и отправляет его на электронную почту пользователя.

        Аргументы:
            request: Объект запроса.

        Возвращает:
            Объект Response. Если активный реферальный код найден, возвращает статус 200 и сообщение о том, что код был отправлен.
            Если активный реферальный код не найден, возвращает статус 404 и сообщение об ошибке.
        """
        
        user = request.user
        email = user.email

        try:
            referral_code = ReferralCode.objects.get(user=user, is_active=True)
        except ReferralCode.DoesNotExist:
            return Response({"message": "No active code found for this user"},
                            status=status.HTTP_404_NOT_FOUND)

        send_mail(
            'Your referral code',
            f'Your referral code is {referral_code.code}',
            SETTINGS.email_host_user,
            [email], 
            fail_silently=False,
        )

        return Response({"message": "Referral code has been sent to the email"},
                        status=status.HTTP_200_OK)
    
    
    @swagger_docs.referral_code_post_schema
    def post(self, request: Request) -> Response:
        """
        Обрабатывает POST-запросы для создания реферального кода пользователя.

        Этот метод получает дату истечения срока действия из запроса, создает новый реферальный код с этой датой истечения
        и делает все другие реферальные коды пользователя неактивными.

        Аргументы:
            request: Объект запроса.

        Возвращает:
            Объект Response. Если реферальный код успешно создан, возвращает статус 201 и данные реферального кода.
            Если дата истечения срока действия не предоставлена или находится в прошлом, возвращает статус 400 и сообщение об ошибке.
        """
        
        user = request.user
        expiry_date = request.data.get("expiry_date")
        

        if not expiry_date:
            return Response({"error": "Expiry date is required"},
                            status=status.HTTP_400_BAD_REQUEST)

        date_object = parser.parse(expiry_date)
        expiry_date = date_object.strftime("%Y-%m-%d")
        
        ReferralCode.objects.filter(user=user, is_active=True).update(is_active=False)

        referral_code = ReferralCode.objects.create(user=user, expiry_date=expiry_date)
        serialize_code = ReferralCodeSerializer(referral_code)
        
        if referral_code.is_expired():
            return Response({"error": "Expiry date must be in the future"},
                            status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serialize_code.data,
                        status=status.HTTP_201_CREATED)
    
    
    @swagger_docs.referral_code_delete_schema
    def delete(self, request: Request) -> Response:
        """
        Обрабатывает DELETE-запросы для удаления активного реферального кода пользователя.

        Этот метод делает активный реферальный код пользователя неактивным.

        Аргументы:
            request: Объект запроса.

        Возвращает:
            Объект Response. Если активный реферальный код успешно удален, возвращает статус 204 и сообщение об успехе.
            Если активный реферальный код не найден, возвращает статус 404 и сообщение об ошибке.
        """
        user = request.user
        try:
            referral_code = ReferralCode.objects.get(user=user, is_active = True)
        except ReferralCode.DoesNotExist:
            return Response({"message": "No active code found"},
                            status=status.HTTP_404_NOT_FOUND)
        
        serialize_code = ReferralCodeSerializer(referral_code)
        ReferralCode.objects.filter(user=user, is_active=True).update(is_active=False)
        return Response({"message": "Code successfully delete",
                        "code": serialize_code.data},
                        status=status.HTTP_204_NO_CONTENT)


class ReferralInfoView(views.APIView):
    """
    API-представление для получения информации о рефералах пользователя.

    Это представление позволяет аутентифицированным пользователям получать информацию о своих рефералах.

    Атрибуты:
        permission_classes: Список классов разрешений, которые должно использовать представление.
    """
    
    permission_classes:list = [IsAuthenticated]
    
    @swagger_docs.referral_code_info_schema
    def get(self, request: Request) -> Response:
        """
        Обрабатывает GET-запросы для получения информации о рефералах пользователя.

        Этот метод получает все рефералы пользователя и возвращает их имена пользователей.

        Аргументы:
            request: Объект запроса.

        Возвращает:
            Объект Response. Возвращает статус 200 и список имен пользователей рефералов.
        """
        
        user = request.user
        referrals = Referral.objects.filter(referrer=user)
        return Response({"referrals": [referral.referral.username for referral in referrals]}, status=status.HTTP_200_OK)
