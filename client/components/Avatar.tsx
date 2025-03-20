import {
  UserCircleIcon,
  CodeBracketIcon,
  BriefcaseIcon,
} from '@heroicons/react/24/solid'
interface AvatarProps {
  role: 'user' | 'pm' | 'developer'
  className?: string
}

const roleIcons = {
  user: <UserCircleIcon className="w-8 h-8 text-amber-500" />,
  pm: <BriefcaseIcon className="w-6 h-6 text-slate-500" />,
  developer: <CodeBracketIcon className="w-6 h-6 text-rose-500" />,
}

export default function Avatar({ role, className }: AvatarProps) {
  return (
    <div
      className={`flex items-center justify-center rounded-full bg-white p-1 ${className}`}>
      {roleIcons[role]}
    </div>
  )
}
