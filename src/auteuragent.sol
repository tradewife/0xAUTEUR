// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

/// @title AuteurAgent8183 — ERC-8183 Agentic Commerce for AUTEUR
/// @notice Job escrow with evaluator attestation for film production services
contract auteuragent {
    using SafeERC20 for IERC20;

    enum JobStatus { OPEN, FUNDED, SUBMITTED, COMPLETED, REJECTED }

    struct Job {
        address client;
        address provider;
        address evaluator;
        address token;
        uint256 amount;
        uint256 expiry;
        JobStatus status;
        bytes32 deliverableHash;
        string deliverableCid;
    }

    uint256 public nextJobId;
    mapping(uint256 => Job) public jobs;
    mapping(address => uint256[]) public clientJobs;
    mapping(address => uint256[]) public providerJobs;

    string[] public capabilities;
    uint256 public pricePerShot;
    address public owner;
    address public auteurAgent;

    event JobCreated(uint256 indexed jobId, address indexed client, address provider, uint256 amount);
    event JobFunded(uint256 indexed jobId, uint256 amount);
    event WorkSubmitted(uint256 indexed jobId, bytes32 deliverableHash, string deliverableCid);
    event JobCompleted(uint256 indexed jobId, bytes32 attestationReason);
    event JobRejected(uint256 indexed jobId, bytes32 attestationReason);
    event JobExpired(uint256 indexed jobId, uint256 refundAmount);
    event AgentCapabilitiesSet(string[] capabilities, uint256 pricePerShot);

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    constructor(address _auteurAgent) {
        owner = msg.sender;
        auteurAgent = _auteurAgent;
        capabilities = ["film_composition", "shot_validation", "mint"];
        pricePerShot = 0.001 ether;
        emit AgentCapabilitiesSet(capabilities, pricePerShot);
    }

    function createJob(
        address provider,
        address evaluator,
        address token,
        uint256 amount,
        uint256 expiry
    ) external returns (uint256 jobId) {
        require(provider == auteurAgent, "Provider must be AUTEUR agent");
        require(evaluator != address(0), "Evaluator required");
        require(amount > 0, "Amount must be > 0");
        require(expiry > block.timestamp, "Expiry must be future");

        jobId = nextJobId++;
        Job storage job = jobs[jobId];
        job.client = msg.sender;
        job.provider = provider;
        job.evaluator = evaluator;
        job.token = token;
        job.amount = amount;
        job.expiry = expiry;
        job.status = JobStatus.OPEN;

        clientJobs[msg.sender].push(jobId);
        providerJobs[provider].push(jobId);

        emit JobCreated(jobId, msg.sender, provider, amount);
    }

    function fundJob(uint256 jobId) external payable {
        Job storage job = jobs[jobId];
        require(msg.sender == job.client, "Only client");
        require(job.status == JobStatus.OPEN, "Must be OPEN");

        if (job.token == address(0)) {
            require(msg.value == job.amount, "Must send exact ETH amount");
        } else {
            require(msg.value == 0, "Use fundJobToken for ERC-20");
        }

        job.status = JobStatus.FUNDED;
        emit JobFunded(jobId, job.amount);
    }

    function fundJobToken(uint256 jobId, uint256 amount) external {
        Job storage job = jobs[jobId];
        require(msg.sender == job.client, "Only client");
        require(job.status == JobStatus.OPEN, "Must be OPEN");
        require(job.token != address(0), "Must be ERC-20 job");
        require(amount == job.amount, "Must send exact amount");

        IERC20(job.token).safeTransferFrom(msg.sender, address(this), amount);
        job.status = JobStatus.FUNDED;
        emit JobFunded(jobId, job.amount);
    }

    function submitWork(
        uint256 jobId,
        bytes32 deliverableHash,
        string calldata deliverableCid
    ) external {
        Job storage job = jobs[jobId];
        require(msg.sender == job.provider, "Only provider");
        require(job.status == JobStatus.FUNDED, "Must be FUNDED");
        require(job.expiry > block.timestamp, "Job expired");

        job.status = JobStatus.SUBMITTED;
        job.deliverableHash = deliverableHash;
        job.deliverableCid = deliverableCid;

        emit WorkSubmitted(jobId, deliverableHash, deliverableCid);
    }

    function completeJob(uint256 jobId, bytes32 attestationReason) external {
        Job storage job = jobs[jobId];
        require(msg.sender == job.evaluator, "Only evaluator");
        require(job.status == JobStatus.SUBMITTED, "Must be SUBMITTED");

        job.status = JobStatus.COMPLETED;

        if (job.token == address(0)) {
            (bool ok, ) = payable(job.provider).call{value: job.amount}("");
            require(ok, "Payment failed");
        } else {
            IERC20(job.token).safeTransfer(job.provider, job.amount);
        }

        emit JobCompleted(jobId, attestationReason);
    }

    function rejectJob(uint256 jobId, bytes32 attestationReason) external {
        Job storage job = jobs[jobId];
        require(msg.sender == job.evaluator, "Only evaluator");
        require(
            job.status == JobStatus.SUBMITTED || job.status == JobStatus.FUNDED,
            "Must be SUBMITTED or FUNDED"
        );

        job.status = JobStatus.REJECTED;

        if (job.token == address(0)) {
            (bool ok, ) = payable(job.client).call{value: job.amount}("");
            require(ok, "Refund failed");
        } else {
            IERC20(job.token).safeTransfer(job.client, job.amount);
        }

        emit JobRejected(jobId, attestationReason);
    }

    function expireJob(uint256 jobId) external {
        Job storage job = jobs[jobId];
        require(job.status == JobStatus.FUNDED, "Must be FUNDED");
        require(block.timestamp >= job.expiry, "Not expired");

        job.status = JobStatus.REJECTED;

        if (job.token == address(0)) {
            (bool ok, ) = payable(job.client).call{value: job.amount}("");
            require(ok, "Refund failed");
        } else {
            IERC20(job.token).safeTransfer(job.client, job.amount);
        }

        emit JobExpired(jobId, job.amount);
    }

    function getCapabilities() external view returns (string[] memory) {
        return capabilities;
    }

    function pricingModel() external view returns (uint256) {
        return pricePerShot;
    }

    function setCapabilities(string[] calldata _capabilities, uint256 _pricePerShot) external onlyOwner {
        capabilities = _capabilities;
        pricePerShot = _pricePerShot;
        emit AgentCapabilitiesSet(_capabilities, _pricePerShot);
    }

    function getJob(uint256 jobId) external view returns (
        address client,
        address provider,
        address evaluator,
        address token,
        uint256 amount,
        uint256 expiry,
        JobStatus status,
        bytes32 deliverableHash,
        string memory deliverableCid
    ) {
        Job storage job = jobs[jobId];
        return (
            job.client,
            job.provider,
            job.evaluator,
            job.token,
            job.amount,
            job.expiry,
            job.status,
            job.deliverableHash,
            job.deliverableCid
        );
    }

    function getClientJobs(address client) external view returns (uint256[] memory) {
        return clientJobs[client];
    }

    function getProviderJobs(address provider) external view returns (uint256[] memory) {
        return providerJobs[provider];
    }

    function contractBalance() external view returns (uint256) {
        return address(this).balance;
    }
}
