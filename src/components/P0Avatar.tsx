import { agencyAvatarSprites } from '@/data/agencyAvatarSprites';
import { douyinAvatarMap, douyinAvatarMeta } from '@/data/douyinAvatarMap';
import { industryAvatarSprites } from '@/data/industryAvatarSprites';
import { useEffect, useState } from 'react';
import tongliHd from '../assets/douyin-hd-6693777798747652109.jpg';
import zhinvHd from '../assets/douyin-hd-6870163473385390093.jpg';
import zhouzhouHd from '../assets/douyin-hd-6912341826695331854.jpg';
import nodeMedicalAvatar from '../assets/node-medical.jpg';

const HD_AVATAR_OVERRIDES: Record<string, string> = {
  '6693777798747652109': tongliHd,
  '6870163473385390093': zhinvHd,
  '6912341826695331854': zhouzhouHd,
};

export type AvatarSprite = {
  avatarUrl: string;
  avatarPosition: string;
  spriteSize: [number, number];
};

type SharedAvatarVisualProps = {
  id: string;
  name: string;
  preferIndustry?: boolean;
};

const DIRECT_NODE_AVATARS: Record<string, string> = {
  '7575570461527015462': nodeMedicalAvatar,
};

// P0 头像图集 3MB+，仅在行业图集未命中时按需加载，避免压进首屏主包。
let cache: Record<string, AvatarSprite> | null = null;
let pending: Promise<void> | null = null;

function useSpriteMap() {
  const [map, setMap] = useState<Record<string, AvatarSprite> | null>(cache);
  useEffect(() => {
    if (cache) return;
    pending ??= import('@/data/p0AvatarSprites').then(module => {
      cache = module.p0AvatarSprites as Record<string, AvatarSprite>;
    });
    let cancelled = false;
    pending
      .then(() => {
        if (!cancelled) setMap(cache);
      })
      .catch(() => {
        // 图集加载失败时回退到代理商头像与姓名兜底，不影响表格。
      });
    return () => {
      cancelled = true;
    };
  }, []);
  return map;
}

function SpriteVisual({
  sprite,
  name,
}: {
  sprite: AvatarSprite;
  name: string;
}) {
  const spriteSize = sprite.spriteSize ??
    douyinAvatarMeta.spriteSize ?? [4000, 3200];
  return (
    <span
      className="avatar-sprite"
      style={{
        backgroundImage: `url(${sprite.avatarUrl})`,
        backgroundPosition: sprite.avatarPosition,
        backgroundSize: `${spriteSize[0]}px ${spriteSize[1]}px`,
      }}
      role="img"
      aria-label={`${name} 头像`}
    />
  );
}

function DeferredAvatarVisual({
  id,
  name,
  preferIndustry,
}: SharedAvatarVisualProps) {
  const sprites = useSpriteMap();
  const [failed, setFailed] = useState(false);
  const sprite = preferIndustry
    ? (sprites?.[id] ?? agencyAvatarSprites[id])
    : (sprites?.[id] ?? industryAvatarSprites[id] ?? agencyAvatarSprites[id]);
  const directAvatar =
    DIRECT_NODE_AVATARS[id] ?? douyinAvatarMap[id]?.avatarUrl;
  const fallback = Array.from(name || '达人')
    .slice(0, 2)
    .join('');

  if (sprite?.avatarPosition)
    return <SpriteVisual sprite={sprite} name={name} />;
  if (!failed && directAvatar) {
    return (
      <img
        src={directAvatar}
        alt={`${name} 头像`}
        onError={() => setFailed(true)}
      />
    );
  }
  return <span>{fallback}</span>;
}

function LegacyAvatarVisual({
  id,
  name,
  preferIndustry = false,
}: SharedAvatarVisualProps) {
  const industrySprite = preferIndustry ? industryAvatarSprites[id] : undefined;
  if (industrySprite) {
    return <SpriteVisual sprite={industrySprite} name={name} />;
  }
  return (
    <DeferredAvatarVisual id={id} name={name} preferIndustry={preferIndustry} />
  );
}

function CachedHdAvatar({
  src,
  ...props
}: SharedAvatarVisualProps & { src: string }) {
  const [failed, setFailed] = useState(false);
  if (failed) return <LegacyAvatarVisual {...props} />;
  return (
    <img
      className="avatar-hd"
      src={src}
      alt={`${props.name} 头像`}
      loading="lazy"
      decoding="async"
      style={{ width: '100%', height: '100%', objectFit: 'cover' }}
      onError={() => setFailed(true)}
    />
  );
}

export function SharedAvatarVisual(props: SharedAvatarVisualProps) {
  const src = HD_AVATAR_OVERRIDES[props.id];
  return src ? (
    <CachedHdAvatar key={`${props.id}-${src}`} src={src} {...props} />
  ) : (
    <LegacyAvatarVisual {...props} />
  );
}

export function P0Avatar({ id, name }: { id: string; name: string }) {
  return (
    <span className="avatar avatar-photo" title={`${name} 头像`}>
      <SharedAvatarVisual id={id} name={name} />
    </span>
  );
}
