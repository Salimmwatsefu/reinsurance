/**
 * DUMMY API CLIENT FOR TESTING
 * 
 * This is a mock implementation that returns fake data.
 * Use this while your backend is loading.
 * 
 * To switch back to real API:
 * 1. Replace this with the real api.ts
 * 2. Update AuthContext to use real authentication
 * 3. Ensure backend is running and configured
 */

// Fake data generators
const generateFakeClaim = (id: number) => ({
  id,
  user_id: 1,
  pdf_filename: `claim_${id}.pdf`,
  status: ['pending', 'processed', 'approved', 'rejected'][Math.floor(Math.random() * 4)],
  created_at: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString(),
  extracted_data: {
    claimant_name: `Claimant ${id}`,
    incident_date: new Date(Date.now() - Math.random() * 90 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    amount_claimed: Math.floor(Math.random() * 100000) + 1000,
    description: `Motor accident claim - ${['collision', 'theft', 'damage', 'liability'][Math.floor(Math.random() * 4)]}`,
  },
  fraud_score: Math.random(),
  is_fraudulent: Math.random() > 0.85,
  reserve_estimate: Math.floor(Math.random() * 80000) + 500,
});

const generateFakePrediction = (claimId: number) => ({
  claim_id: claimId,
  fraud_score: Math.random(),
  is_fraudulent: Math.random() > 0.85,
  reserve_estimate: Math.floor(Math.random() * 80000) + 500,
  model_version: 'v1.2.0',
});

class DummyApiClient {
  /**
   * Simulate network delay
   */
  private async delay(ms: number = 500) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  // ============================================
  // Authentication endpoints (dummy)
  // ============================================

  async login(email: string, password: string) {
    await this.delay(1000);
    return {
      access_token: 'dummy-token-' + Math.random().toString(36).substr(2, 9),
      user: {
        id: 1,
        email,
        first_name: email.split('@')[0],
        last_name: 'Demo',
        role: email.includes('admin') ? 'admin' : 'insurer',
      },
    };
  }

  async register(data: {
    email: string;
    password: string;
    first_name: string;
    last_name: string;
    role: string;
  }) {
    await this.delay(1000);
    return {
      message: 'User created successfully',
      user: {
        id: Math.floor(Math.random() * 10000),
        ...data,
      },
    };
  }

  async getUserProfile() {
    await this.delay(500);
    return {
      user: {
        id: 1,
        email: 'demo@example.com',
        first_name: 'Demo',
        last_name: 'User',
        role: 'insurer',
      },
    };
  }

  async logout() {
    await this.delay(500);
    return { message: 'Logout successful' };
  }

  // ============================================
  // Claims endpoints (dummy)
  // ============================================

  async uploadClaim(file: File) {
    await this.delay(2000); // Simulate processing
    const claimId = Math.floor(Math.random() * 10000);
    return {
      message: 'Claim processed successfully',
      claim: generateFakeClaim(claimId),
      prediction: generateFakePrediction(claimId),
    };
  }

  async getClaims(params?: {
    page?: number;
    limit?: number;
    status?: string;
  }) {
    await this.delay(500);
    const page = params?.page || 1;
    const limit = params?.limit || 10;
    const total = 47; // Fake total

    // Generate fake claims
    const claims = Array.from({ length: limit }, (_, i) => {
      const claimId = (page - 1) * limit + i + 1;
      return generateFakeClaim(claimId);
    });

    // Filter by status if provided
    const filtered = params?.status
      ? claims.filter((c) => c.status === params.status)
      : claims;

    return {
      claims: filtered,
      total,
      page,
      limit,
    };
  }

  async getClaim(claimId: number) {
    await this.delay(500);
    return generateFakeClaim(claimId);
  }

  async updateClaimStatus(claimId: number, status: string) {
    await this.delay(500);
    return {
      id: claimId,
      status,
      updated_at: new Date().toISOString(),
    };
  }

  async deleteClaim(claimId: number) {
    await this.delay(500);
    return {};
  }

  async getPrediction(claimId: number) {
    await this.delay(500);
    return generateFakePrediction(claimId);
  }

  // ============================================
  // Reports endpoints (dummy)
  // ============================================

  async getClaimsReport(params?: {
    start_date?: string;
    end_date?: string;
    status?: string;
  }) {
    await this.delay(800);
    return {
      total_claims: 127,
      fraudulent_count: 12,
      avg_fraud_score: 0.32,
      avg_reserve: 15420,
      status_breakdown: {
        pending: 23,
        processed: 67,
        approved: 28,
        rejected: 9,
      },
    };
  }

  async getFraudTrends(params?: {
    group_by?: string;
    start_date?: string;
    end_date?: string;
  }) {
    await this.delay(800);
    return {
      trends: [
        { range: '$0-$5,000', fraud_count: 2, total_count: 45 },
        { range: '$5,001-$10,000', fraud_count: 3, total_count: 38 },
        { range: '$10,001-$50,000', fraud_count: 4, total_count: 32 },
        { range: '$50,001-$100,000', fraud_count: 2, total_count: 10 },
        { range: '$100,001+', fraud_count: 1, total_count: 2 },
      ],
    };
  }

  // ============================================
  // Model endpoints (dummy)
  // ============================================

  async getModels() {
    await this.delay(500);
    return [
      {
        model_name: 'fraud_classifier_v1',
        model_type: 'fraud',
        metrics: {
          accuracy: 0.92,
          recall: 0.85,
          precision: 0.88,
          f1: 0.86,
        },
        status: 'active',
        trained_at: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
      },
      {
        model_name: 'reserve_estimator_v1',
        model_type: 'reserve',
        metrics: {
          mse: 2450,
          mae: 1200,
          r2: 0.78,
        },
        status: 'active',
        trained_at: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
      },
    ];
  }

  async getModel(modelName: string) {
    await this.delay(500);
    return {
      model_name: modelName,
      model_type: modelName.includes('fraud') ? 'fraud' : 'reserve',
      metrics: {
        accuracy: 0.92,
        recall: 0.85,
        precision: 0.88,
        f1: 0.86,
      },
      status: 'active',
      trained_at: new Date().toISOString(),
    };
  }

  async retrainModel(data: { model_name: string; model_type: string }) {
    await this.delay(3000); // Simulate training
    return {
      message: `${data.model_name} retrained successfully`,
    };
  }
}

export const api = new DummyApiClient();
