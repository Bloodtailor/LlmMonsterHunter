// useMonsterChat.js - The whole home-base chat state machine for ONE monster
// Loads the persistent thread, sends messages (optimistic), streams the
// monster's reply token-by-token (workflow step emit_generation_id ->
// chat_text_generation_id), appends the final reply on workflow.completed,
// and surfaces "will remember this" moments from monster.memory_added
// events whose source is the home chat.

import { useCallback, useEffect, useRef, useState } from 'react';
import { sendChatMessage, getChatHistory } from '../../../api/services/chat.js';
import { useEventSubscription } from '../../../api/events/useEventSubscription.js';
import { useStreamedGeneration } from '../../../api/events/useStreamedGeneration.js';

// How long a "will remember this" toast lingers
const MEMORY_TOAST_MS = 8000;

/**
 * Hook managing one monster's chat thread
 * @param {number|null} monsterId - The selected chat partner (null = none)
 * @returns {object} Thread state and actions
 */
export function useMonsterChat(monsterId) {
  const [messages, setMessages] = useState([]); // [{id, role, text}]
  const [hasMore, setHasMore] = useState(false);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const [isReplying, setIsReplying] = useState(false); // waiting on the monster
  const [streamingText, setStreamingText] = useState('');
  const [error, setError] = useState(null);
  const [memoryToasts, setMemoryToasts] = useState([]); // [{id, kind, content}]

  // The partner the in-flight events belong to (avoids stale closures)
  const monsterIdRef = useRef(monsterId);
  monsterIdRef.current = monsterId;
  const toastTimersRef = useRef([]);

  // ===== HISTORY =====

  const loadHistory = useCallback(async (id) => {
    setIsLoadingHistory(true);
    setError(null);
    try {
      const page = await getChatHistory(id);
      // The partner may have changed while the request was in flight
      if (monsterIdRef.current !== id) return;
      setMessages(page.messages);
      setHasMore(page.hasMore);
    } catch (loadError) {
      if (monsterIdRef.current === id) {
        setError(loadError?.message || 'Could not load the conversation');
      }
    } finally {
      if (monsterIdRef.current === id) {
        setIsLoadingHistory(false);
      }
    }
  }, []);

  const loadOlder = useCallback(async () => {
    const id = monsterIdRef.current;
    if (!id || !messages.length) return;
    try {
      const page = await getChatHistory(id, { beforeId: messages[0].id });
      if (monsterIdRef.current !== id) return;
      setMessages((prev) => [...page.messages, ...prev]);
      setHasMore(page.hasMore);
    } catch (loadError) {
      setError(loadError?.message || 'Could not load older messages');
    }
  }, [messages]);

  // A fresh partner means a fresh thread view
  useEffect(() => {
    setMessages([]);
    setHasMore(false);
    setStreamingText('');
    setIsReplying(false);
    setError(null);
    if (monsterId) {
      loadHistory(monsterId);
    }
  }, [monsterId, loadHistory]);

  // Toast timers die with the hook
  useEffect(
    () => () => {
      toastTimersRef.current.forEach(clearTimeout);
    },
    [],
  );

  // ===== SENDING =====

  const send = useCallback(
    async (text) => {
      const id = monsterIdRef.current;
      const spoken = String(text || '').trim();
      if (!id || !spoken || isReplying) return;

      setError(null);
      setIsReplying(true);
      // Optimistic: the adventurer's words appear immediately
      const optimisticKey = `pending-${Date.now()}`;
      setMessages((prev) => [...prev, { id: optimisticKey, role: 'player', text: spoken }]);

      try {
        await sendChatMessage(id, spoken);
      } catch (sendError) {
        // The backend refused (not at home base, too long...) - the line
        // was never stored, so it comes back out of the thread
        setMessages((prev) => prev.filter((message) => message.id !== optimisticKey));
        setIsReplying(false);
        setError(sendError?.message || 'The message could not be sent');
      }
    },
    [isReplying],
  );

  // ===== THE REPLY, STREAMING IN =====

  useStreamedGeneration('chat_text_generation_id', {
    onText: (partialText) => setStreamingText(partialText),
  });

  useEventSubscription('workflowCompleted', ({ workflowItem, result }) => {
    if (workflowItem?.workflowType !== 'chat_with_monster') return;
    if (!result || result.monster_id !== monsterIdRef.current) return;
    setStreamingText('');
    setIsReplying(false);
    if (result.reply) {
      setMessages((prev) => [
        ...prev,
        {
          id: `reply-${Date.now()}`,
          role: 'monster',
          text: result.reply,
        },
      ]);
    }
  });

  useEventSubscription('workflowFailed', ({ workflowItem, error: failure }) => {
    if (workflowItem?.workflowType !== 'chat_with_monster') return;
    setStreamingText('');
    setIsReplying(false);
    const detail = typeof failure === 'string' ? failure : failure?.error;
    setError(detail || 'The monster lost its words - try again');
  });

  // ===== "WILL REMEMBER THIS" MOMENTS =====
  // chat_housekeeping saves memories AFTER the reply; each one lands as
  // a monster.memory_added event stamped source: home_chat

  useEventSubscription('monsterMemoryAdded', ({ monsterId: eventMonsterId, memory }) => {
    if (!memory || eventMonsterId !== monsterIdRef.current) return;
    if (memory.details?.source !== 'home_chat') return;

    setMemoryToasts((prev) => [...prev.slice(-2), memory]);
    const timer = setTimeout(() => {
      setMemoryToasts((prev) => prev.filter((toast) => toast.id !== memory.id));
    }, MEMORY_TOAST_MS);
    toastTimersRef.current.push(timer);
  });

  return {
    messages,
    hasMore,
    isLoadingHistory,
    isReplying,
    streamingText,
    error,
    memoryToasts,
    send,
    loadOlder,
  };
}
