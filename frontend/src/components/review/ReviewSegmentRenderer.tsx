import { getChangeClass, getSegmentTooltip } from "./reviewSegmentUtils";
import type { ReviewSegment } from "./reviewSegmentUtils";

type Props = {
  segments: ReviewSegment[];
  onSegmentClick?: (issueId?: string) => void;
};

export default function ReviewSegmentRenderer({ segments, onSegmentClick }: Props) {
  return (
    <div className="review-segment-container">
      {segments.map((segment) => (
        <span
          key={segment.id}
          className={getChangeClass(segment.type)}
          title={getSegmentTooltip(segment)}
          onClick={() => onSegmentClick?.(segment.issueId)}
        >
          {segment.text}
        </span>
      ))}
    </div>
  );
}
