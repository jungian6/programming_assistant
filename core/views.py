from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import StreamingHttpResponse
from openai import OpenAI
from typing import Iterator
from .models import Message


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('chat')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('chat')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})


@login_required
def chat_view(request):
    messages = Message.objects.filter(user=request.user)
    return render(request, 'chat.html', {'messages': messages})


def get_chat_history(user) -> list:
    """Get formatted chat history for the user"""
    messages = []
    # Add system message first
    messages.append({
        "role": "system",
        "content": "You are a helpful and knowledgeable AI assistant. You provide accurate, informative responses while maintaining a friendly and professional tone."
    })

    # Add user chat history
    for message in Message.objects.filter(user=user).order_by('timestamp'):
        messages.append({"role": "user", "content": message.user_message})
        messages.append({"role": "assistant", "content": message.ai_message})

    return messages


@login_required
def generate_completion(request, user_prompt: str) -> StreamingHttpResponse:
    """Stream OpenAI completion back to the client"""

    def complete_with_openai() -> Iterator[str]:
        client = OpenAI(
        api_key="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"
        )
        # Get chat history and add current prompt
        messages = get_chat_history(request.user)
        messages.append({"role": "user", "content": user_prompt})

        stream = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            stream=True,
        )

        # Store the complete AI response
        complete_response = ""

        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content is not None:
                complete_response += content
                # Format content for browser display
                formatted_content = content.replace("\n", "<br>")
                formatted_content = formatted_content.replace(",", ", ")
                formatted_content = formatted_content.replace(".", ". ")
                yield f"data: {formatted_content}\n\n"

        # Save the complete message pair to the database
        Message.objects.create(
            user=request.user,
            user_message=user_prompt,
            ai_message=complete_response
        )

    return StreamingHttpResponse(complete_with_openai(), content_type="text/event-stream")


def home(request):
    if request.user.is_authenticated:
        return redirect('chat')
    return render(request, 'home.html')
