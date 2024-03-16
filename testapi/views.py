import requests
import swagger_docs 
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
    permission_classes = [AllowAny]


    @swagger_docs.user_registration_schema
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get("email")
            response = requests.get(f"https://api.hunter.io/v2/email-verifier?email={email}&api_key={SETTINGS.eh_api_key}")
            
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
    permission_classes = [AllowAny]
    
    
    @swagger_docs.user_login_schema
    def post(self, request):
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
    permission_classes = (IsAuthenticated,)


    @swagger_docs.referral_code_get_schema
    def get(self, request):
        
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
    def post(self, request):
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
    def delete(self, request):
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
    permission_classes = [IsAuthenticated]
    @swagger_docs.referral_code_info_schema
    def get(self, request):
        user = request.user
        referrals = Referral.objects.filter(referrer=user)
        return Response({"referrals": [referral.referral.username for referral in referrals]}, status=status.HTTP_200_OK)
