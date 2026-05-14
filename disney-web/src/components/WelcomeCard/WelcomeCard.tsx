import './WelcomeCard.css'

const SUGGESTIONS = [
  { label: '万圣节有什么活动？', value: '万圣节有什么特别活动？' },
  { label: '邮轮价格查询', value: '迪士尼邮轮的价格是多少？' },
  { label: '快速通行证怎么用', value: '园区快速通行证怎么用？' },
  { label: '巡游演出时间', value: '最近的巡游演出时间表' },
]

export interface WelcomeCardProps {
  onSelect: (value: string) => void
}

export function WelcomeCard({ onSelect }: WelcomeCardProps) {
  return (
    <div className="welcome-card">
      <div className="welcome-icon">✦</div>
      <h3>欢迎来到迪士尼魔法世界</h3>
      <p>
        我是您的智能客服助手，可以帮您查询门票价格、演出时间、活动海报等信息。试试下面的问题：
      </p>
      <div className="welcome-suggestions">
        {SUGGESTIONS.map((s) => (
          <button
            key={s.value}
            className="welcome-suggestion"
            onClick={() => onSelect(s.value)}
          >
            {s.label}
          </button>
        ))}
      </div>
    </div>
  )
}
