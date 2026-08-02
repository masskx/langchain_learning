import Header from './components/Header'
import ChatArea from './components/ChatArea'
import InputArea from './components/InputArea'
import { useChat } from './hooks/useChat'

export default function App() {
  const {
    messages,
    isStreaming,
    uploading,
    sendMessage,
    newSession,
    uploadFile,
  } = useChat()

  return (
    <div className="min-h-screen relative">
      {/* 背景层 */}
      <div className="fixed inset-0 bg-gradient-to-br from-amber-50 via-orange-50/50 to-rose-50/30" />
      <div className="fixed inset-0 opacity-40 pointer-events-none">
        <div className="absolute top-20 left-10 w-72 h-72 bg-amber-200 rounded-full mix-blend-multiply blur-3xl animate-pulse-soft" />
        <div className="absolute top-40 right-10 w-96 h-96 bg-orange-200 rounded-full mix-blend-multiply blur-3xl animate-pulse-soft" style={{ animationDelay: '1s' }} />
        <div className="absolute bottom-20 left-1/3 w-80 h-80 bg-rose-200 rounded-full mix-blend-multiply blur-3xl animate-pulse-soft" style={{ animationDelay: '2s' }} />
      </div>

      {/* 内容层 */}
      <div className="relative flex flex-col min-h-screen">
        <Header
          onNewSession={newSession}
          disabled={isStreaming}
        />

        <ChatArea
          messages={messages}
          isStreaming={isStreaming}
        />

        <InputArea
          onSend={sendMessage}
          onUpload={uploadFile}
          isStreaming={isStreaming}
          uploading={uploading}
        />
      </div>
    </div>
  )
}
