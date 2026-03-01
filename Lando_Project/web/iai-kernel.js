/**
 * IAI Kernel
 * Layer selection pipeline:
 *  Input -> EMD(cost model) -> IRL -> ILL -> CLL
 */

export class IAIKernel {
  constructor({ irl, ill, cll, tau = 0.72 } = {}) {
    this.irl = irl;
    this.ill = ill;
    this.cll = cll;
    this.tau = tau;
  }

  async respond(query) {
    const energyBudget = this.computeCost(query);

    const irl = await this.irl.evaluate(query, energyBudget);
    if (irl.confidence >= this.tau) {
      return this._result('IRL', irl.answer, irl.confidence, irl.cost);
    }

    const ill = await this.ill.retrieve(query, energyBudget);
    if (ill.confidence >= this.tau) {
      return this._result('ILL', ill.answer, ill.confidence, ill.cost);
    }

    const cll = await this.cll.generate(query, {
      energyBudget,
      priorCandidates: ill.candidates || [],
    });
    return this._result('CLL', cll.answer, cll.confidence ?? 1.0, cll.cost);
  }

  computeCost(query) {
    const tokens = query.trim().split(/\s+/).filter(Boolean).length;
    const heuristicCost = 1;
    const retrievalCost = 2 + Math.ceil(tokens / 12);
    const llmCost = 8 + Math.ceil(tokens / 4);

    return {
      tokens,
      heuristicCost,
      retrievalCost,
      llmCost,
      preferredLayer: tokens < 24 ? 'IRL' : 'ILL',
    };
  }

  _result(layer, answer, confidence, cost) {
    return {
      layer,
      answer,
      confidence,
      cost,
      ts: Date.now(),
    };
  }
}
