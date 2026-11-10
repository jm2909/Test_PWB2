import { resetDatabase } from './_reset_db';

export default function globalSetup(): void {
  resetDatabase();
}
