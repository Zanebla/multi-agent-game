import {
  UserCircleIcon,
  CodeBracketIcon,
  BriefcaseIcon,
  CogIcon,
} from '@heroicons/react/24/solid'
interface AvatarProps {
  role: 'USER' | 'PM' | 'SDE' | 'SYS'
  className?: string
}

const roleIcons = {
  USER: <UserCircleIcon className="w-8 h-8 text-amber-500" />,
  PM: <BriefcaseIcon className="w-6 h-6 text-slate-500" />,
  SDE: <CodeBracketIcon className="w-6 h-6 text-rose-500" />,
  SYS: <CogIcon className="w-6 h-6 text-gray-500" />,
}

export default function Avatar({ role, className }: AvatarProps) {
  return (
    <div
      className={`flex items-center justify-center rounded-full bg-white p-1 ${className}`}>
      {roleIcons[role]}
    </div>
  )
}
