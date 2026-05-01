type Props = {
  message?: string;
  requestId?: string;
};

export default function ErrorAlert({ message, requestId }: Props) {
  if (!message) return null;
  return (
    <div className="error-box">
      <strong>审稿失败：</strong>{message}
      {requestId ? <div>request_id：{requestId}</div> : null}
    </div>
  );
}
