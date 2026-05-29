<template>
    <div class="chatbot-view">
        <div class="chatbot-container">
            <!-- Header -->
            <div class="chat-header">
                <div class="agent-info">
                    <div class="agent-avatar">
                        <Icon name="boot_2" :size="30" />
                    </div>
                    <div class="agent-details">
                        <h3>Asistente Virtual</h3>
                        <div class="status">En línea</div>
                    </div>
                </div>
                <div class="chat-actions">
                    <button class="btn-ghost icon-btn" @click="clearChat" title="Limpiar chat">
                        <Icon name="trash-2" :size="18" />
                    </button>
                    <button
                        v-if="isStreaming"
                        class="btn-ghost icon-btn"
                        @click="stopStreaming"
                        title="Detener respuesta"
                    >
                        <Icon name="x" :size="18" />
                    </button>
                    <!-- <button class="btn-ghost icon-btn" title="Configuración">
                        <Icon name="settings" :size="18" />
                    </button> -->
                </div>
            </div>

            <!-- Messages -->
            <div class="chat-messages" ref="messagesContainer">
                <div v-for="(msg, index) in messages" :key="index" class="message" :class="`message-${msg.type}`">
                    <div v-if="msg.type === 'agent'" class="agent-avatar-small">
                        <!-- Optional small avatar for repeated messages -->
                    </div>

                    <div class="message-bubble">
                        <div class="markdown-content" v-html="renderMessage(msg.text)"></div>

                        <!-- Reasoning Section -->
                        <div v-if="msg.reasoning" class="mt-2 pt-2 border-t border-gray-600/30 text-xs text-gray-400">
                            <details>
                                <summary class="cursor-pointer hover:text-primary transition-colors">Ver razonamiento</summary>
                                <div class="mt-1 p-2 bg-black/10 rounded whitespace-pre-wrap font-mono text-[10px]">
                                    {{ msg.reasoning }}
                                </div>
                            </details>
                        </div>
                    </div>
                    <span class="message-time">{{ formatTime(msg.timestamp) }}</span>
                </div>
            </div>

            <!-- Typing Indicator -->
            <div class="typing-indicator" :style="{ visibility: isTyping ? 'visible' : 'hidden' }">
                {{ isStreaming ? 'Recibiendo respuesta en tiempo real' : 'Asistente escribiendo' }}<span>.</span><span>.</span><span>.</span>
            </div>

            <!-- Input Area -->
            <div class="chat-input-area">
                <div class="input-wrapper">
                    <textarea
                        v-model="newMessage"
                        placeholder="Escribe tu mensaje aquí..."
                        @keydown.enter.prevent="sendMessage"
                        ref="messageInput"
                        rows="1"
                    ></textarea>
                </div>
                <button class="btn-send" @click="sendMessage" :disabled="!newMessage.trim() || isTyping">
                    <Icon name="send" :size="20" />
                </button>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, inject } from 'vue';
import Icon from '@/components/Icon.vue';
import apiClient from '@/services/api/client';
import { buildApiUrl } from '@/services/api/url';
import { marked } from 'marked';
import hljs from 'highlight.js/lib/core';
import javascript from 'highlight.js/lib/languages/javascript';
import typescript from 'highlight.js/lib/languages/typescript';
import json from 'highlight.js/lib/languages/json';
import bash from 'highlight.js/lib/languages/bash';
import python from 'highlight.js/lib/languages/python';
import xml from 'highlight.js/lib/languages/xml';
import css from 'highlight.js/lib/languages/css';
import sql from 'highlight.js/lib/languages/sql';
import 'highlight.js/styles/github-dark.css'; // Import highlight.js theme

hljs.registerLanguage('javascript', javascript);
hljs.registerLanguage('js', javascript);
hljs.registerLanguage('typescript', typescript);
hljs.registerLanguage('ts', typescript);
hljs.registerLanguage('json', json);
hljs.registerLanguage('bash', bash);
hljs.registerLanguage('sh', bash);
hljs.registerLanguage('shell', bash);
hljs.registerLanguage('python', python);
hljs.registerLanguage('py', python);
hljs.registerLanguage('xml', xml);
hljs.registerLanguage('html', xml);
hljs.registerLanguage('css', css);
hljs.registerLanguage('sql', sql);

// Configure marked with highlight.js
marked.setOptions({
    highlight: function(code, lang) {
        const language = hljs.getLanguage(lang) ? lang : 'plaintext';
        return hljs.highlight(code, { language }).value;
    },
    langPrefix: 'hljs language-', // highlight.js css expects a top-level 'hljs' class.
});

const messagesContainer = ref(null);
const messageInput = ref(null);
const newMessage = ref('');
const isTyping = ref(false);
const isStreaming = ref(false);
const streamAbortController = ref(null);

const messages = ref([
    {
        type: 'agent',
        text: '¡Hola! Soy tu asistente virtual impulsado por IA. ¿En qué puedo ayudarte hoy?',
        timestamp: new Date()
    }
]);

const layoutConfig = inject('layoutConfig');

const renderMessage = (text) => {
    // Basic sanitization could be added here if needed, but marked handles most.
    // However, for chatbots, we trust the model output mostly, but strictly sanitizing user input if reflected back.
    // Since this is a local simulated chatbot, marked is generally safe enough for now.
    try {
        return marked.parse(text);
    } catch (e) {
        console.error("Markdown parsing error:", e);
        return text;
    }
};

onMounted(() => {
    scrollToBottom();
    // Disable fit-screen to allow our custom container to handle height
    // and rely on the calc() css.
    if (layoutConfig && layoutConfig.fitContentToScreen) {
        layoutConfig.fitContentToScreen.value = false;
    }
});

onMounted(() => {
    // Focus input on load
    if (messageInput.value) {
        messageInput.value.focus();
    }
});

const formatTime = (date) => {
    return new Date(date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

const scrollToBottom = () => {
    nextTick(() => {
        if (messagesContainer.value) {
            messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
        }
    });
};

const parseStandardChatResponse = (responseData) => {
    let reply = 'No pude procesar la respuesta.';
    let reasoning = null;

    if (responseData.output && Array.isArray(responseData.output)) {
        const messageObj = responseData.output.find(item => item.type === 'message');
        const reasoningObj = responseData.output.find(item => item.type === 'reasoning');

        if (messageObj && messageObj.content) {
            reply = messageObj.content;
        }

        if (reasoningObj && reasoningObj.content) {
            reasoning = reasoningObj.content;
        }
    } else if (typeof responseData === 'string') {
        reply = responseData;
    } else if (responseData.choices && responseData.choices[0]?.message?.content) {
        reply = responseData.choices[0].message.content;
    }

    return { reply, reasoning };
};

const consumeSSE = async (response, assistantMessage) => {
    if (!response.body) {
        throw new Error('El servidor no envió stream de respuesta.');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let sseBuffer = '';
    let streamCompleted = false;

    while (!streamCompleted) {
        const { done, value } = await reader.read();
        if (done) {
            break;
        }

        sseBuffer += decoder.decode(value, { stream: true });

        let eventEndPos;
        while ((eventEndPos = sseBuffer.indexOf('\n\n')) !== -1) {
            const rawEvent = sseBuffer.slice(0, eventEndPos);
            sseBuffer = sseBuffer.slice(eventEndPos + 2);

            const lines = rawEvent.split(/\r?\n/);
            let eventName = 'message';
            const dataLines = [];

            for (const line of lines) {
                if (line.startsWith('event:')) {
                    eventName = line.slice(6).trim();
                }

                if (line.startsWith('data:')) {
                    dataLines.push(line.slice(5).trim());
                }
            }

            const dataPayload = dataLines.join('\n');
            if (!dataPayload) {
                continue;
            }

            if (eventName === 'done' || dataPayload === '[DONE]') {
                streamCompleted = true;
                break;
            }

            if (eventName === 'token') {
                try {
                    const tokenData = JSON.parse(dataPayload);
                    if (tokenData.text) {
                        assistantMessage.text += tokenData.text;
                        scrollToBottom();
                    }
                } catch {
                    assistantMessage.text += dataPayload;
                    scrollToBottom();
                }
                continue;
            }

            if (eventName === 'error') {
                try {
                    const errorData = JSON.parse(dataPayload);
                    throw new Error(errorData.message || 'Error en stream de IA.');
                } catch {
                    throw new Error('Error en stream de IA.');
                }
            }
        }
    }
};

const requestNonStreamFallback = async (contextInput, assistantMessage) => {
    const response = await apiClient.post('/auth/chatbot/chat', {
        input: contextInput,
    });

    const { reply, reasoning } = parseStandardChatResponse(response.data);
    assistantMessage.text = reply;
    assistantMessage.reasoning = reasoning;
};

const stopStreaming = () => {
    if (streamAbortController.value) {
        streamAbortController.value.abort();
    }
};

const handleGlobalKeydown = (event) => {
    if (event.key === 'Escape' && isStreaming.value) {
        stopStreaming();
    }
};

onUnmounted(() => {
    window.removeEventListener('keydown', handleGlobalKeydown);
    stopStreaming();
});

onMounted(() => {
    window.addEventListener('keydown', handleGlobalKeydown);
});

const sendMessage = async () => {
    const text = newMessage.value.trim();
    if (!text || isTyping.value) return;

    // Add user message
    messages.value.push({
        type: 'user',
        text: text,
        timestamp: new Date()
    });

    newMessage.value = '';
    scrollToBottom();

    // Call Local AI API
    isTyping.value = true;

    // Construct context from recent messages to maintain conversation history
    const recentMessages = messages.value.slice(-10); // Keep last 10 messages for context
    let contextInput = "";

    recentMessages.forEach(msg => {
        if (msg.type === 'user') {
            contextInput += `User: ${msg.text}\n`;
        } else if (msg.type === 'agent') {
            contextInput += `Assistant: ${msg.text}\n`;
        }
    });

    // The current new message is already in 'messages' array because we pushed it at the start of sendMessage
    // But we need to make sure we don't duplicate it or leave it out if logic changes.
    // In current logic: messages.value.push({ type: 'user', text }) happens BEFORE this block.
    // So recentMessages INCLUDES the current user message at the end.
    // However, the loop above adds "User: text" for it.
    // So contextInput ALREADY contains the current query at the end.

    // We send the whole conversation history as input so the model sees it all.
    // But wait, if the model expects "input" as the *prompt*, passing the whole dialogue is correct for completion.
    // If it expects "Last user message" separately, this might be redundant.
    // Given it's a "chat" endpoint, sending the full transcript usually works for maintaining context in completion-style models.

    const assistantMessage = {
        type: 'agent',
        text: '',
        reasoning: null,
        timestamp: new Date(),
    };
    messages.value.push(assistantMessage);

    try {
        const controller = new AbortController();
        streamAbortController.value = controller;
        isStreaming.value = true;

        const token = localStorage.getItem('token');
        const streamResponse = await fetch(buildApiUrl('auth/chatbot/stream'), {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                Accept: 'text/event-stream',
                ...(token ? { Authorization: `Bearer ${token}` } : {}),
            },
            body: JSON.stringify({ input: contextInput }),
            signal: controller.signal,
        });

        if (!streamResponse.ok) {
            throw new Error(`Error de stream (${streamResponse.status})`);
        }

        await consumeSSE(streamResponse, assistantMessage);

        if (!assistantMessage.text.trim()) {
            await requestNonStreamFallback(contextInput, assistantMessage);
        }
    } catch (error) {
        if (error?.name === 'AbortError') {
            if (!assistantMessage.text.trim()) {
                messages.value.pop();
            }
            messages.value.push({
                type: 'system',
                text: 'Respuesta detenida por el usuario.',
                timestamp: new Date()
            });
            return;
        }

        try {
            await requestNonStreamFallback(contextInput, assistantMessage);
        } catch {
            messages.value.pop();
            console.error('AI Error:', error);
            messages.value.push({
                type: 'system',
                text: `Error al conectar con la IA: ${error.message}. Asegúrate de que el servidor local esté corriendo en el puerto 1234.`,
                timestamp: new Date()
            });
        }

    } finally {
        isStreaming.value = false;
        streamAbortController.value = null;
        isTyping.value = false;
        scrollToBottom();
    }
};

const clearChat = () => {
    stopStreaming();
    messages.value = [
        {
            type: 'system',
            text: 'El chat ha sido limpiado.',
            timestamp: new Date()
        },
        {
            type: 'agent',
            text: '¡Hola! Soy tu asistente virtual impulsado por IA. ¿En qué puedo ayudarte hoy?',
            timestamp: new Date()
        }
    ];
};
</script>

<style lang="scss" scoped>
// Scoped styles if needed override global chatbot styles
// But mostly handled in _chatbot.scss
</style>
