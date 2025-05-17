export async function GET() {
  return Response.json({ webhookUrl: process.env.TWILIO_WEBHOOK_URL });
}
