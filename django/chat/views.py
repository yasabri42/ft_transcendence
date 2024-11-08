from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Room, Message
from users.models import FriendList
from django.http import JsonResponse
from django.contrib.auth.models import User
from users.models import Profile
from django.views.decorators.csrf import csrf_exempt
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from game.models import Party
import json

# Create your views here.
@login_required
def chat_page(request):
    profile = Profile.objects.all()
    rooms = Room.objects.all()
    users = User.objects.all()
    current_user = request.user
    if current_user.is_authenticated:
        try:
            friend_list = FriendList.objects.get(user=current_user)
            friends = friend_list.friends.all()
        except FriendList.DoesNotExist:
            friends = None

    return render(request, "chat/chat.html", {
        "rooms": rooms,
        "users" : users,
        "profiles": profile,
        "friends" : friends,
        })

def room(request, slug):
    room_name=Room.objects.get(slug=slug).name
    messages=Message.objects.filter(room=Room.objects.get(slug=slug))

    username1, username2 = slug.split('_')
    other_username = username2 if request.user.username == username1 else username1
    other_user = get_object_or_404(User, username=other_username)
    profile = get_object_or_404(Profile, user=other_user)
    context = {"slug":slug, "room_name":room_name, 'messages':messages, 'user_id':request.user.id, 'profile':profile, 'other_user_id':other_user.id}
    return render(request, "chat/room.html", context)

def create_room(request):
    if request.method == "POST":
        # Assuming 'name' and 'slug' are provided in the form submission
        name = request.POST.get('name')
        slug = request.POST.get('slug')
        user1 = request.user
        user2_id = request.POST.get('user2_id')
        user2 = User.objects.get(id=user2_id)

        # Ensure consistent order of usernames for room slug
        user1_username = user1.username
        user2_username = user2.username
        room_slug = '_'.join(sorted([user1_username, user2_username]))

        existing_room = Room.objects.filter(slug=room_slug).exists()
        if not existing_room:
            # Create a new room
            room = Room.objects.create(name=name, slug=room_slug, user1=user1, user2=user2)
            return redirect('chat:room', slug=room_slug)
        else:
            # Room already exists, redirect to the existing room
            return redirect('chat:room', slug=room_slug)

@login_required
@csrf_exempt  # Be cautious with csrf_exempt; ensure security
def send_game_invite(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        room_slug = data.get('room_slug')
        if not room_slug:
            return JsonResponse({'status': 'error', 'message': 'Room slug not provided'})

        # Get the usernames from the room slug
        usernames = room_slug.split('_')
        if len(usernames) != 2:
            return JsonResponse({'status': 'error', 'message': 'Invalid room slug'})

        sender = request.user
        other_username = usernames[0] if usernames[1] == sender.username else usernames[1]
        other_user = get_object_or_404(User, username=other_username)

        # Create the party
        party = Party.objects.create(
            creator=sender,
            num_players=2,
            status='active'
        )
        party.participants.add(sender, other_user)

        # Send the invitation via the channel layer
        channel_layer = get_channel_layer()
        room_group_name = f'chat_{room_slug}'
        async_to_sync(channel_layer.group_send)(
            room_group_name, {
                'type': 'game_invite',
                'sender': sender.username,
                'recipient': other_user.username,
                'party_id': party.id
            }
        )

        return JsonResponse({'status': 'success', 'party_id': party.id})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
